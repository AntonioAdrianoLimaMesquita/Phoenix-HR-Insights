"""Build dimension tables and a coherent employee population."""
from __future__ import annotations

from datetime import timedelta
import random
import numpy as np
import pandas as pd

from config import Settings
from generator import POSITION_RULES, ORGANIZATION_BLUEPRINT, LOCATIONS, EDUCATION_WEIGHTS, RACES


FEMALE_FIRST_NAMES = ["Ana", "Beatriz", "Camila", "Carolina", "Daniela", "Fernanda", "Gabriela", "Juliana", "Larissa", "Mariana", "Patrícia", "Renata", "Sofia", "Tatiana", "Vanessa"]
MALE_FIRST_NAMES = ["André", "Bruno", "Carlos", "Daniel", "Eduardo", "Felipe", "Gustavo", "Henrique", "João", "Leandro", "Marcelo", "Paulo", "Rafael", "Ricardo", "Thiago"]
LAST_NAMES = ["Almeida", "Barbosa", "Cardoso", "Costa", "Ferreira", "Gomes", "Lima", "Martins", "Mendes", "Oliveira", "Pereira", "Ribeiro", "Rodrigues", "Santos", "Silva", "Souza"]


def _weighted(rng: random.Random, rows):
    values, weights = zip(*[(row, row[-1]) for row in rows])
    return rng.choices(values, weights=weights, k=1)[0]


def build_calendar(settings: Settings) -> pd.DataFrame:
    dates = pd.date_range(settings.start_date, settings.end_date, freq="D")
    frame = pd.DataFrame({"Date": dates})
    frame["CalendarKey"] = frame["Date"].dt.strftime("%Y%m%d").astype(int)
    frame["Year"] = frame["Date"].dt.year
    frame["Quarter"] = "Q" + frame["Date"].dt.quarter.astype(str)
    frame["MonthNumber"] = frame["Date"].dt.month
    frame["MonthName"] = frame["Date"].dt.month_name()
    frame["YearMonth"] = frame["Date"].dt.strftime("%Y-%m")
    frame["MonthStart"] = frame["Date"].dt.to_period("M").dt.start_time.dt.date
    frame["MonthEnd"] = frame["Date"].dt.to_period("M").dt.end_time.dt.date
    frame["FiscalYear"] = frame["Year"]
    return frame


def build_organizations(settings: Settings) -> pd.DataFrame:
    rows = []
    key = 1
    for vp, directorate, department, area, weight in ORGANIZATION_BLUEPRINT:
        for team_no in range(1, 5):
            rows.append({"OrganizationKey": key, "Company": settings.company_name, "VicePresidency": vp,
                         "Directorate": directorate, "Department": department, "Area": area,
                         "Team": f"{area} Team {team_no}", "TurnoverRiskFactor": 1.25 if directorate == "Commercial" else (1.15 if directorate == "Operations" else 0.85),
                         "AllocationWeight": weight / 4})
            key += 1
    return pd.DataFrame(rows)


def build_positions() -> pd.DataFrame:
    return pd.DataFrame([{"PositionKey": i + 1, "JobTitle": p.title, "CareerLevel": p.career_level,
                           "JobFamily": p.job_family, "IsLeadership": p.leadership, "SalaryMin": p.salary_min,
                           "SalaryMidpoint": p.salary_mid, "SalaryMax": p.salary_max,
                           "TargetBonusPct": p.bonus_target, "PLRMonths": p.plr_months}
                         for i, p in enumerate(POSITION_RULES)])


def build_locations() -> pd.DataFrame:
    return pd.DataFrame([{"LocationKey": i + 1, "State": item[0], "City": item[1], "Region": item[2], "AllocationWeight": item[3]}
                         for i, item in enumerate(LOCATIONS)])


def build_compensation_bands(positions: pd.DataFrame) -> pd.DataFrame:
    frame = positions[["PositionKey", "JobTitle", "SalaryMin", "SalaryMidpoint", "SalaryMax", "TargetBonusPct", "PLRMonths"]].copy()
    frame.insert(0, "CompensationKey", range(1, len(frame) + 1))
    return frame


def build_employees(settings: Settings, organizations: pd.DataFrame, positions: pd.DataFrame, locations: pd.DataFrame) -> pd.DataFrame:
    rng = random.Random(settings.seed)
    org_rows = organizations.to_dict("records")
    org_weights = organizations["AllocationWeight"].tolist()
    loc_rows = locations.to_dict("records")
    loc_weights = locations["AllocationWeight"].tolist()
    position_rows = positions.to_dict("records")
    position_weights = [0.02, 0.09, 0.21, 0.22, 0.18, 0.08, 0.07, 0.07, 0.035, 0.012, 0.003]
    rows = []
    latest_hire = settings.end_date - timedelta(days=25)
    earliest_hire = pd.Timestamp("2002-01-01").date()
    for key in range(1, settings.employee_count + 1):
        gender = rng.choices(["Female", "Male", "Non-binary"], weights=[0.47, 0.51, 0.02], k=1)[0]
        first_name = rng.choice(FEMALE_FIRST_NAMES if gender == "Female" else MALE_FIRST_NAMES)
        name = f"{first_name} {rng.choice(LAST_NAMES)} {rng.choice(LAST_NAMES)}"
        birth = pd.Timestamp("1963-01-01").date() + timedelta(days=rng.randint(0, (pd.Timestamp("2004-12-31").date() - pd.Timestamp("1963-01-01").date()).days))
        hire = earliest_hire + timedelta(days=rng.randint(0, (latest_hire - earliest_hire).days))
        org = rng.choices(org_rows, weights=org_weights, k=1)[0]
        position = rng.choices(position_rows, weights=position_weights, k=1)[0]
        location = rng.choices(loc_rows, weights=loc_weights, k=1)[0]
        education = _weighted(rng, EDUCATION_WEIGHTS)[0]
        race = _weighted(rng, RACES)[0]
        pcd = rng.random() < 0.06
        terminated = hire < settings.end_date - timedelta(days=45) and rng.random() < 0.13
        termination_min = max(hire + timedelta(days=35), settings.start_date)
        termination_date = termination_min + timedelta(days=rng.randint(0, max(0, (settings.end_date - termination_min).days))) if terminated else None
        end_of_service = termination_date or settings.end_date
        age_at_end = int((end_of_service - birth).days / 365.25)
        if position["CareerLevel"] in {"Director", "Executive"} and age_at_end < 35:
            birth = birth - timedelta(days=(35 - age_at_end) * 365)
        rows.append({"EmployeeKey": key, "EmployeeID": f"PFG{key:06d}", "FullName": name, "Gender": gender,
                     "BirthDate": birth, "MaritalStatus": rng.choices(["Single", "Married", "Divorced", "Widowed"], [0.40, 0.47, 0.11, 0.02])[0],
                     "Children": max(0, int(rng.gauss(1.0, 1.0))), "Education": education, "Race": race, "IsPCD": pcd,
                     "HireDate": hire, "TerminationDate": termination_date, "EmploymentStatus": "Inactive" if terminated else "Active",
                     "WorkModel": rng.choices(["Hybrid", "On-site", "Remote"], [0.61, 0.28, 0.11])[0],
                     "Email": f"{key:06d}@phoenix.example", "OrganizationKey": org["OrganizationKey"],
                     "PositionKey": position["PositionKey"], "LocationKey": location["LocationKey"]})
    return pd.DataFrame(rows)


def build_managers(employees: pd.DataFrame, positions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    leaders = employees.merge(positions[["PositionKey", "JobTitle", "CareerLevel", "IsLeadership"]], on="PositionKey")
    leaders = leaders[leaders["IsLeadership"]].copy()
    leaders = leaders.sort_values(["OrganizationKey", "PositionKey", "EmployeeKey"])
    manager_lookup = leaders.groupby("OrganizationKey").head(12).copy()
    manager_lookup["ManagerKey"] = range(1, len(manager_lookup) + 1)
    manager_lookup["HierarchyLevel"] = manager_lookup["CareerLevel"]
    manager_dim = manager_lookup[["ManagerKey", "EmployeeKey", "EmployeeID", "FullName", "OrganizationKey", "HierarchyLevel"]].rename(columns={"EmployeeKey": "ManagerEmployeeKey", "EmployeeID": "ManagerID", "FullName": "ManagerName"})
    assignments = []
    available = manager_lookup.groupby("OrganizationKey")["ManagerKey"].apply(list).to_dict()
    for row in employees.itertuples(index=False):
        managers = available.get(row.OrganizationKey, manager_dim["ManagerKey"].tolist())
        assignments.append(managers[(row.EmployeeKey - 1) % len(managers)])
    employees = employees.copy()
    employees["ManagerKey"] = assignments
    return manager_dim.reset_index(drop=True), employees


def build_dimensions(settings: Settings) -> dict[str, pd.DataFrame]:
    calendar = build_calendar(settings)
    organizations = build_organizations(settings)
    positions = build_positions()
    locations = build_locations()
    employees = build_employees(settings, organizations, positions, locations)
    managers, employees = build_managers(employees, positions)
    compensation = build_compensation_bands(positions)
    return {"d_calendar": calendar, "d_employee": employees, "d_organization": organizations, "d_position": positions,
            "d_location": locations, "d_manager": managers, "d_compensation": compensation}
