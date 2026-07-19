# Phoenix HR Insights — Business Case

## Context

Phoenix Financial Group is a fictional national financial-services organization with approximately 15,000 employees. HR, Finance and leadership teams use separate operational reports, which makes it difficult to monitor workforce health and act quickly on risks.

## Problem statement

Leadership needs a consistent view of workforce composition, employee movements, turnover, compensation and engagement. The current reporting process is fragmented, manual and does not connect indicators to business decisions.

## Product objective

Phoenix HR Insights is a People Analytics data product that consolidates synthetic HR data into a dimensional warehouse ready for SQL Server and Power BI. It supports executive analysis without exposing real employee information.

## Decisions supported

- Identify turnover concentration by organization, position and leadership chain.
- Monitor headcount, hiring, terminations and internal mobility over time.
- Evaluate compensation positioning, bonus and PLR accruals.
- Identify engagement, absenteeism and overtime risk signals.
- Track diversity and representation in leadership roles.
- Compare training investment with workforce and talent indicators.

## Scope

The initial release provides a reproducible Python generator, CSV warehouse tables, SQL Server DDL and documentation. A Power BI semantic model and executive report can consume these outputs in the next sprint.

## Privacy and ethics

Every record is synthetic. Names, employee IDs, emails, compensation values and events are generated for demonstration only. The project must not be used to make employment decisions about real people or as a substitute for appropriate privacy, governance and bias-review processes.
