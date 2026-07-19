# Phoenix HR Insights

Synthetic People Analytics data warehouse for portfolio demonstrations. The project models a fictional financial-services company and creates coherent employee, organization, compensation, workforce snapshot, movement, termination, and training data.

All records are generated locally and are fictional. No real employee, customer, or company data is used.

## Quick start

```powershell
cd Phoenix-HR-Insights
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\python\main.py --employees 15000 --start 2024-01-01 --end 2026-06-30
```

The command writes CSV tables to `data/processed/`, SQL Server DDL to `sql/create_tables.sql`, and a run summary to `data/processed/run_summary.json`.

For a lighter development run:

```powershell
python .\python\main.py --employees 500 --start 2025-01-01 --end 2025-12-31
```

## Generated tables

Dimensions: `d_calendar`, `d_employee`, `d_organization`, `d_position`, `d_location`, `d_manager`, `d_compensation`.

Facts: `f_workforce`, `f_movements`, `f_terminations`, `f_training`.

`f_workforce` is a monthly snapshot. It is intentionally the largest table and supports headcount, compensation, engagement, absenteeism, overtime, diversity, and talent analyses.

## Documentation

- [Business case](docs/business_case.md)
- [Architecture and data lineage](docs/architecture.md)
- [Data dictionary](docs/data_dictionary.md)
- [KPI catalog](docs/kpi_catalog.md)
