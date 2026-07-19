"""Create fact tables from the synthetic dimensions using business rules."""
from __future__ import annotations

from datetime import timedelta
import random
import numpy as np
import pandas as pd

from config import Settings


def _month_ends(start, end):
    return pd.date_range(start, end, freq="ME").date


def build_workforce(settings: Settings, dims: dict[str, pd.DataFrame]) -> pd.DataFrame:
    employees = dims["d_employee"].copy()
    positions = dims["d_position"]
    orgs = dims["d_organization"]
    base = employees.merge(positions, on="PositionKey", how="left").merge(
        orgs[["OrganizationKey", "Directorate", "TurnoverRiskFactor"]], on="OrganizationKey"
    )
    rng = np.random.default_rng(settings.seed + 1)
    snapshots = []
    for month_end in _month_ends(settings.start_date, settings.end_date):
        active = base[(base["HireDate"] <= month_end) & ((base["TerminationDate"].isna()) | (base["TerminationDate"] > month_end))].copy()
        tenure = ((pd.Timestamp(month_end) - pd.to_datetime(active["HireDate"])).dt.days / 365.25).clip(lower=0)
        age = ((pd.Timestamp(month_end) - pd.to_datetime(active["BirthDate"])).dt.days / 365.25).astype(int)
        compa = np.clip(rng.normal(1.0, 0.10, len(active)) + np.minimum(tenure, 10) * 0.004, 0.80, 1.20)
        salary = (active["SalaryMidpoint"].to_numpy() * compa).round(2)
        performance = np.clip(rng.normal(3.35, 0.62, len(active)), 1, 5).round(1)
        engagement_base = 72 - (active["TurnoverRiskFactor"].to_numpy() - 1) * 12 + (performance - 3) * 4
        engagement = np.clip(rng.normal(engagement_base, 8), 35, 100).round(1)
        overtime_mean = np.where(active["Directorate"].eq("Commercial"), 11, np.where(active["Directorate"].eq("Operations"), 13, 6))
        overtime = np.clip(rng.normal(overtime_mean, 4, len(active)), 0, 40).round(1)
        absenteeism = np.clip(rng.gamma(1.8, np.where(active["Directorate"].eq("Operations"), 2.2, 1.3), len(active)), 0, 32).round(1)
        bonus = (salary * active["TargetBonusPct"].to_numpy() / 12 * (0.7 + performance / 10)).round(2)
        plr = (salary * active["PLRMonths"].to_numpy() / 12).round(2)
        frame = pd.DataFrame({"SnapshotDate": month_end, "CalendarKey": int(pd.Timestamp(month_end).strftime("%Y%m%d")),
                              "EmployeeKey": active["EmployeeKey"].to_numpy(), "OrganizationKey": active["OrganizationKey"].to_numpy(),
                              "PositionKey": active["PositionKey"].to_numpy(), "ManagerKey": active["ManagerKey"].to_numpy(),
                              "LocationKey": active["LocationKey"].to_numpy(), "CompensationKey": active["PositionKey"].to_numpy(),
                              "Age": age.to_numpy(), "TenureYears": tenure.round(2).to_numpy(), "BaseSalary": salary,
                              "CompaRatio": compa.round(3), "MonthlyBonusAccrual": bonus, "MonthlyPLRAccrual": plr,
                              "BenefitsCost": (salary * 0.22).round(2), "OvertimeHours": overtime, "AbsenteeismHours": absenteeism,
                              "EngagementScore": engagement, "PerformanceScore": performance,
                              "TrainingHoursYTD": np.clip(rng.normal(18 + performance * 5, 8, len(active)), 0, 120).round(1),
                              "TurnoverRiskScore": np.clip(100 - engagement + overtime * 1.2 + absenteeism * 0.8 - performance * 4, 1, 99).round(1)})
        snapshots.append(frame)
    result = pd.concat(snapshots, ignore_index=True)
    result.insert(0, "WorkforceFactKey", range(1, len(result) + 1))
    return result


def build_terminations(settings: Settings, dims: dict[str, pd.DataFrame]) -> pd.DataFrame:
    emp = dims["d_employee"].dropna(subset=["TerminationDate"]).copy()
    rng = np.random.default_rng(settings.seed + 2)
    rows = []
    reasons_voluntary = ["Career opportunity", "Compensation", "Manager relationship", "Work-life balance", "Relocation"]
    reasons_involuntary = ["Performance", "Restructuring", "Policy violation", "End of contract"]
    for row in emp.itertuples(index=False):
        voluntary = rng.random() < 0.63
        reason = rng.choice(reasons_voluntary if voluntary else reasons_involuntary)
        tenure = max(0.1, (row.TerminationDate - row.HireDate).days / 365.25)
        estimated_salary = 8500 * (1 + min(tenure, 8) * 0.05)
        rows.append({"TerminationFactKey": len(rows) + 1, "TerminationDate": row.TerminationDate,
                     "CalendarKey": int(pd.Timestamp(row.TerminationDate).strftime("%Y%m%d")), "EmployeeKey": row.EmployeeKey,
                     "OrganizationKey": row.OrganizationKey, "PositionKey": row.PositionKey, "ManagerKey": row.ManagerKey,
                     "TerminationType": "Voluntary" if voluntary else "Involuntary", "TerminationReason": reason,
                     "TenureAtTerminationYears": round(tenure, 2), "ReplacementDays": int(rng.integers(25, 95)),
                     "EstimatedTurnoverCost": round(estimated_salary * rng.uniform(0.8, 1.8), 2)})
    return pd.DataFrame(rows)


def build_movements(settings: Settings, dims: dict[str, pd.DataFrame]) -> pd.DataFrame:
    emp = dims["d_employee"].copy()
    rng = np.random.default_rng(settings.seed + 3)
    candidates = emp[emp["HireDate"] <= settings.end_date - timedelta(days=180)]
    rows = []
    for row in candidates.itertuples(index=False):
        if rng.random() > 0.16:
            continue
        movement_date = max(row.HireDate + timedelta(days=180), settings.start_date)
        if movement_date > settings.end_date:
            continue
        event_date = pd.Timestamp(movement_date) + pd.Timedelta(days=int(rng.integers(0, max(1, (pd.Timestamp(settings.end_date) - pd.Timestamp(movement_date)).days))))
        event_type = rng.choice(["Promotion", "Salary adjustment", "Internal transfer", "Manager change"], p=[0.34, 0.34, 0.18, 0.14])
        rows.append({"MovementFactKey": len(rows) + 1, "MovementDate": event_date.date(), "CalendarKey": int(event_date.strftime("%Y%m%d")),
                     "EmployeeKey": row.EmployeeKey, "OrganizationKey": row.OrganizationKey, "PositionKey": row.PositionKey,
                     "ManagerKey": row.ManagerKey, "MovementType": event_type,
                     "SalaryIncreasePct": round(float(rng.uniform(0.05, 0.18) if event_type in {"Promotion", "Salary adjustment"} else 0), 3),
                     "IsPromotion": event_type == "Promotion"})
    return pd.DataFrame(rows)


def build_training(settings: Settings, dims: dict[str, pd.DataFrame]) -> pd.DataFrame:
    emp = dims["d_employee"]
    rng = np.random.default_rng(settings.seed + 4)
    catalog = [("Data Literacy", 8, 350), ("Leadership Essentials", 16, 1200), ("Compliance & Ethics", 4, 120),
               ("Customer Experience", 6, 260), ("Python for Analytics", 24, 1800), ("Inclusive Leadership", 6, 420)]
    rows = []
    sample = emp.sample(n=int(len(emp) * 1.65), replace=True, random_state=settings.seed)
    for row in sample.itertuples(index=False):
        course, hours, cost = catalog[int(rng.integers(0, len(catalog)))]
        completed = pd.Timestamp(rng.integers(pd.Timestamp(settings.start_date).value, pd.Timestamp(settings.end_date).value)).date()
        if completed < row.HireDate or (pd.notna(row.TerminationDate) and completed > row.TerminationDate):
            continue
        rows.append({"TrainingFactKey": len(rows) + 1, "CompletionDate": completed, "CalendarKey": int(pd.Timestamp(completed).strftime("%Y%m%d")),
                     "EmployeeKey": row.EmployeeKey, "OrganizationKey": row.OrganizationKey, "CourseName": course,
                     "TrainingHours": hours, "TrainingCost": cost, "Completed": True, "Certification": course in {"Python for Analytics", "Leadership Essentials"}})
    return pd.DataFrame(rows)


def build_facts(settings: Settings, dims: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {"f_workforce": build_workforce(settings, dims), "f_terminations": build_terminations(settings, dims),
            "f_movements": build_movements(settings, dims), "f_training": build_training(settings, dims)}
