# Architecture and Data Lineage

## Logical flow

```text
Business rules + seeded random generator
                 |
                 v
Python dimension generator ----> d_* CSV tables
                 |
                 +-------------> fact generator ----> f_* CSV tables
                                                        |
                                                        v
                                                SQL Server staging / DW
                                                        |
                                                        v
                                              Power BI semantic model
                                                        |
                                                        v
                                               Executive HR dashboard
```

## Design choices

The warehouse uses a star-schema approach. Conformed dimensions describe employees, organization, position, location, managers, compensation bands and calendar dates. Fact tables record a monthly workforce snapshot and operational events.

`f_workforce` has one record per active employee at each month-end. This makes historical headcount, compensation, engagement and risk analysis possible without overwriting past values.

## Table relationships

| Fact table | Grain | Main foreign keys |
|---|---|---|
| `f_workforce` | Active employee at month-end | Calendar, employee, organization, position, manager, location, compensation |
| `f_terminations` | One termination event | Calendar, employee, organization, position, manager |
| `f_movements` | One internal movement event | Calendar, employee, organization, position, manager |
| `f_training` | One completed training record | Calendar, employee, organization |

## Reproducibility

The default seed is set in `python/config.py`. Running the generator with the same employee count, date range and seed produces the same logical scenario, making results repeatable for portfolio demonstrations.

## Loading sequence

1. Create the target schema with `sql/create_tables.sql`.
2. Load dimensions before facts.
3. Load `f_workforce`, `f_terminations`, `f_movements` and `f_training`.
4. Validate key coverage and row counts against `data/processed/run_summary.json`.
5. Connect Power BI to the warehouse and create one-to-many relationships from each dimension to its corresponding facts.
