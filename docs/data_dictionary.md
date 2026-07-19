# Data Dictionary

## Dimensions

| Table | Key | Purpose | Selected fields |
|---|---|---|---|
| `d_calendar` | `CalendarKey` | Date intelligence | Date, Year, Quarter, MonthName, YearMonth, FiscalYear |
| `d_employee` | `EmployeeKey` | Synthetic employee profile and employment lifecycle | EmployeeID, Gender, BirthDate, Education, Race, IsPCD, HireDate, TerminationDate, WorkModel |
| `d_organization` | `OrganizationKey` | Organizational hierarchy | VicePresidency, Directorate, Department, Area, Team, TurnoverRiskFactor |
| `d_position` | `PositionKey` | Role and career architecture | JobTitle, CareerLevel, JobFamily, IsLeadership, SalaryMin, SalaryMidpoint, SalaryMax |
| `d_location` | `LocationKey` | Geographic hierarchy | State, City, Region |
| `d_manager` | `ManagerKey` | Leadership chain | ManagerID, ManagerName, OrganizationKey, HierarchyLevel |
| `d_compensation` | `CompensationKey` | Compensation reference bands | SalaryMin, SalaryMidpoint, SalaryMax, TargetBonusPct, PLRMonths |

## Facts

| Table | Grain | Measures and attributes |
|---|---|---|
| `f_workforce` | One active employee per month-end | BaseSalary, CompaRatio, MonthlyBonusAccrual, MonthlyPLRAccrual, BenefitsCost, OvertimeHours, AbsenteeismHours, EngagementScore, PerformanceScore, TrainingHoursYTD, TurnoverRiskScore |
| `f_terminations` | One employee termination | TerminationType, TerminationReason, TenureAtTerminationYears, ReplacementDays, EstimatedTurnoverCost |
| `f_movements` | One employee movement | MovementType, SalaryIncreasePct, IsPromotion |
| `f_training` | One completed course per employee | CourseName, TrainingHours, TrainingCost, Completed, Certification |

## Business rules embedded in the generator

- Compensation is based on position salary bands; senior roles have higher variable-pay targets.
- Commercial and Operations teams receive higher simulated overtime and turnover-risk factors.
- Termination, movement and training events only occur inside each employee's simulated employment period.
- Workforce snapshots include only employees active on the month-end date.
- Approximately 6% of the generated workforce is represented as persons with disabilities (PCD); demographics are synthetic distributions for analytical demonstration only.
