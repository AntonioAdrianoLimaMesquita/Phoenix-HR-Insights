"""Reusable reference data and business rules for the synthetic company."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PositionRule:
    title: str
    career_level: str
    job_family: str
    leadership: bool
    salary_min: int
    salary_mid: int
    salary_max: int
    bonus_target: float
    plr_months: float


POSITION_RULES = [
    PositionRule("Intern", "Intern", "Corporate", False, 1_400, 1_700, 2_000, 0.00, 0.0),
    PositionRule("Assistant", "Entry", "Operations", False, 2_200, 2_800, 3_500, 0.03, 0.4),
    PositionRule("Analyst I", "Junior", "Specialist", False, 3_800, 4_800, 6_000, 0.05, 0.7),
    PositionRule("Analyst II", "Mid", "Specialist", False, 5_500, 7_000, 8_800, 0.08, 0.9),
    PositionRule("Senior Analyst", "Senior", "Specialist", False, 7_500, 9_500, 12_000, 0.12, 1.1),
    PositionRule("Specialist", "Specialist", "Specialist", False, 10_000, 13_000, 16_500, 0.15, 1.3),
    PositionRule("Coordinator", "Coordinator", "Leadership", True, 11_500, 14_500, 18_000, 0.18, 1.4),
    PositionRule("Manager", "Manager", "Leadership", True, 16_000, 21_000, 27_000, 0.25, 1.8),
    PositionRule("Senior Manager", "Senior Manager", "Leadership", True, 23_000, 30_000, 38_000, 0.30, 2.0),
    PositionRule("Director", "Director", "Leadership", True, 35_000, 47_000, 62_000, 0.40, 2.5),
    PositionRule("Executive Director", "Executive", "Leadership", True, 55_000, 75_000, 100_000, 0.50, 3.0),
]


ORGANIZATION_BLUEPRINT = [
    ("Retail Banking", "Commercial", "Sales", "Retail Sales", 0.20),
    ("Retail Banking", "Commercial", "Branch Network", "Branch Operations", 0.15),
    ("Corporate Banking", "Commercial", "Middle Market", "Corporate Coverage", 0.11),
    ("Digital Banking", "Technology", "Engineering", "Digital Products", 0.12),
    ("Digital Banking", "Technology", "Data & AI", "Data Platform", 0.07),
    ("Operations", "Operations", "Service", "Customer Operations", 0.12),
    ("Risk & Compliance", "Risk", "Risk Management", "Credit Risk", 0.06),
    ("Finance", "Finance", "Controllership", "FP&A", 0.04),
    ("People & Culture", "People", "People Analytics", "Rewards & Analytics", 0.04),
    ("Legal & Compliance", "Legal", "Legal Affairs", "Labor Relations", 0.02),
    ("Corporate", "Corporate", "Strategy", "Transformation Office", 0.03),
    ("Wealth Management", "Investments", "Advisory", "Private Banking", 0.04),
]

LOCATIONS = [
    ("SP", "São Paulo", "Southeast", 0.55), ("RJ", "Rio de Janeiro", "Southeast", 0.14),
    ("MG", "Belo Horizonte", "Southeast", 0.09), ("PR", "Curitiba", "South", 0.07),
    ("RS", "Porto Alegre", "South", 0.05), ("BA", "Salvador", "Northeast", 0.04),
    ("PE", "Recife", "Northeast", 0.03), ("DF", "Brasília", "Central-West", 0.03),
]

EDUCATION_WEIGHTS = [("High School", 0.12), ("Bachelor's", 0.48), ("Postgraduate", 0.30), ("Master's", 0.08), ("PhD", 0.02)]
RACES = [("White", 0.45), ("Brown", 0.36), ("Black", 0.13), ("Asian", 0.04), ("Indigenous", 0.02)]


def weighted_choice(rng, values):
    """Return one item from tuples where the final item is its relative weight."""
    choices = [item[:-1] if len(item) > 2 else item[0] for item in values]
    weights = [item[-1] for item in values]
    return rng.choices(choices, weights=weights, k=1)[0]
