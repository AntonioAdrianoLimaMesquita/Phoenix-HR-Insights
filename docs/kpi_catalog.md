# KPI Catalog

| KPI | Definition | Recommended calculation | Decision use |
|---|---|---|---|
| Headcount | Active employees at the selected month-end | Distinct count of `EmployeeKey` in `f_workforce` | Workforce capacity planning |
| Hires | Employees with `HireDate` in the selected period | Count of employees by HireDate | Recruiting demand and growth |
| Terminations | Employees whose termination occurred in the period | Count of `TerminationFactKey` | Attrition monitoring |
| Turnover rate | Departures compared with average workforce | Terminations / average headcount | Retention and organizational health |
| Voluntary turnover | Employee-initiated departures | Voluntary terminations / average headcount | Employee experience and market competitiveness |
| Average tenure | Average service length of active employees | Average `TenureYears` | Workforce maturity and retention |
| Promotion rate | Promotions relative to active workforce | Promotion movements / average headcount | Internal mobility and talent development |
| Average salary | Average monthly base salary | Average `BaseSalary` | Compensation planning |
| Compa-ratio | Pay position against band midpoint | Average `CompaRatio` | Pay equity and salary-range governance |
| Turnover cost | Estimated financial impact of departures | Sum `EstimatedTurnoverCost` | Prioritization of retention actions |
| Absenteeism hours | Recorded absence hours | Sum `AbsenteeismHours` | Workforce wellbeing and operational capacity |
| Engagement score | Simulated employee engagement index | Average `EngagementScore` | Engagement interventions |
| Female leadership | Representation of women in leadership | Female leaders / all leaders | Diversity and inclusion monitoring |
| Training investment | Course spend in the selected period | Sum `TrainingCost` | Learning and development planning |

## Important interpretation note

The metrics are calculated from synthetic data and demonstrate analytical design only. In a real implementation, formulas, thresholds, benchmarks, legal definitions and eligibility rules must be agreed with HR, Finance, Legal and Data Governance stakeholders.
