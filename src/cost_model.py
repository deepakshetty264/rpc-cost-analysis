"""
Cost model for a residential activity centre.

Implements the methodology in docs/methodology.md:

    Step 1  timing     -> annual cost per line (capital depreciated)
    Step 2  scope      -> filter by whether the cost belongs in the pricing base
    Step 3  behaviour  -> fixed / variable pools
    Step 4  volume     -> bed-nights as the activity driver
    Step 5  break-even -> cost per bed-night, compared to price per bed-night

All modelling judgements are exposed as configuration rather than hard-coded,
so their effect on the result can be demonstrated instead of assumed.

Expects input files in data/ (gitignored) following docs/data_schema.md.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"


# ----------------------------------------------------------------------
# Configuration — the modelling judgements, in one place
# ----------------------------------------------------------------------
@dataclass
class Config:
    # Timing: how capital is charged to the year
    capital_treatment: str = "depreciate"      # full | depreciate | exclude
    default_useful_life: int = 5
    useful_lives: dict[str, int] = field(default_factory=dict)

    # Scope: which costs pricing is expected to recover
    cost_scope: str = "all"                    # all | pricing_only

    # Volume: what fixed costs are spread over
    fixed_allocation_base: str = "all"         # all | chargeable

    # Operating context
    days_open: int = 365
    occupied_days: int | None = None           # for the daily-cost view

    def validate(self) -> None:
        if self.capital_treatment not in {"full", "depreciate", "exclude"}:
            raise ValueError(f"bad capital_treatment: {self.capital_treatment}")
        if self.cost_scope not in {"all", "pricing_only"}:
            raise ValueError(f"bad cost_scope: {self.cost_scope}")
        if self.fixed_allocation_base not in {"all", "chargeable"}:
            raise ValueError(f"bad fixed_allocation_base: {self.fixed_allocation_base}")


# ----------------------------------------------------------------------
# Step 1–3: cost pools
# ----------------------------------------------------------------------
def annualise(costs: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Convert each cost line to an annual figure (Step 1: timing)."""
    df = costs.copy()
    is_capital = df["is_capital"].astype(str).str.upper().eq("Y")

    if cfg.capital_treatment == "full":
        df["annual_cost"] = df["value"]
    elif cfg.capital_treatment == "exclude":
        df["annual_cost"] = np.where(is_capital, 0.0, df["value"])
    else:  # depreciate
        lives = df["item"].map(cfg.useful_lives).fillna(cfg.default_useful_life)
        df["annual_cost"] = np.where(is_capital, df["value"] / lives, df["value"])

    return df


def build_pools(costs: pd.DataFrame, cfg: Config) -> tuple[float, float, pd.DataFrame]:
    """Return (fixed_pool, variable_pool, annualised_frame)."""
    df = annualise(costs, cfg)

    if cfg.cost_scope == "pricing_only":                       # Step 2: scope
        df = df[df["affects_pricing"].astype(str).str.upper().eq("Y")]

    category = df["cost_category"].astype(str).str.title()     # Step 3: behaviour
    fixed = df.loc[category.eq("Fixed"), "annual_cost"].sum()
    variable = df.loc[category.eq("Variable"), "annual_cost"].sum()
    return float(fixed), float(variable), df


# ----------------------------------------------------------------------
# Step 4–5: volume and break-even
# ----------------------------------------------------------------------
def bed_nights(bookings: pd.DataFrame, chargeable_only: bool = False) -> float:
    """Total bed-nights. Set chargeable_only to exclude non-commercial use."""
    df = bookings
    if chargeable_only and "is_chargeable" in df.columns:
        df = df[df["is_chargeable"].astype(str).str.upper().eq("Y")]
    return float((df["people"] * df["nights"]).sum())


def break_even(costs: pd.DataFrame, bookings: pd.DataFrame, cfg: Config) -> dict:
    """Break-even cost per bed-night under the given configuration."""
    cfg.validate()
    fixed, variable, _ = build_pools(costs, cfg)

    total_bn = bed_nights(bookings)
    if total_bn <= 0:
        raise ValueError("no bed-nights in booking data")

    base_bn = (
        total_bn
        if cfg.fixed_allocation_base == "all"
        else bed_nights(bookings, chargeable_only=True)
    )

    fixed_per_bn = fixed / base_bn
    variable_per_bn = variable / total_bn

    return {
        "fixed_pool": fixed,
        "variable_pool": variable,
        "total_cost": fixed + variable,
        "total_bed_nights": total_bn,
        "allocation_base_bed_nights": base_bn,
        "fixed_per_bed_night": fixed_per_bn,
        "variable_per_bed_night": variable_per_bn,
        "break_even_per_bed_night": fixed_per_bn + variable_per_bn,
    }


def daily_cost(costs: pd.DataFrame, cfg: Config) -> dict:
    """Cost of an unoccupied day versus an occupied one."""
    if not cfg.occupied_days:
        raise ValueError("set Config.occupied_days for the daily-cost view")
    fixed, variable, _ = build_pools(costs, cfg)
    unoccupied = fixed / cfg.days_open
    increment = variable / cfg.occupied_days
    return {
        "unoccupied_day": unoccupied,
        "occupied_day": unoccupied + increment,
        "variable_increment": increment,
    }


def recovery(price_per_bed_night: float, break_even_per_bed_night: float) -> float:
    """Ratio below 1.0 indicates pricing below full cost.

    Both sides must already be expressed per bed-night — comparing a
    per-course tariff against a per-bed-night cost is the single most
    common error in this analysis.
    """
    if break_even_per_bed_night <= 0:
        raise ValueError("break-even must be positive")
    return price_per_bed_night / break_even_per_bed_night


# ----------------------------------------------------------------------
# Scenario grid
# ----------------------------------------------------------------------
def scenario_grid(costs: pd.DataFrame, bookings: pd.DataFrame) -> pd.DataFrame:
    """Break-even across every combination of the three modelling switches.

    Reporting the grid rather than a point estimate is deliberate: it shows
    how sensitive the result is to judgements that are not facts.
    """
    rows = []
    for capital in ("full", "depreciate", "exclude"):
        for scope in ("all", "pricing_only"):
            for base in ("all", "chargeable"):
                cfg = Config(
                    capital_treatment=capital,
                    cost_scope=scope,
                    fixed_allocation_base=base,
                )
                result = break_even(costs, bookings, cfg)
                rows.append(
                    {
                        "capital": capital,
                        "scope": scope,
                        "fixed_base": base,
                        "break_even_per_bed_night": result["break_even_per_bed_night"],
                        "total_cost": result["total_cost"],
                    }
                )
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--costs", default=DATA / "costs.csv")
    parser.add_argument("--bookings", default=DATA / "bookings.csv")
    parser.add_argument("--grid", action="store_true", help="print the scenario grid")
    args = parser.parse_args()

    costs = pd.read_csv(args.costs)
    bookings = pd.read_csv(args.bookings)

    cfg = Config()
    result = break_even(costs, bookings, cfg)

    print(f"Configuration : capital={cfg.capital_treatment}, "
          f"scope={cfg.cost_scope}, fixed_base={cfg.fixed_allocation_base}")
    print("-" * 58)
    print(f"Fixed pool               {result['fixed_pool']:>14,.2f}")
    print(f"Variable pool            {result['variable_pool']:>14,.2f}")
    print(f"Total cost               {result['total_cost']:>14,.2f}")
    print(f"Total bed-nights         {result['total_bed_nights']:>14,.0f}")
    print("-" * 58)
    print(f"Fixed / bed-night        {result['fixed_per_bed_night']:>14,.2f}")
    print(f"Variable / bed-night     {result['variable_per_bed_night']:>14,.2f}")
    print(f"BREAK-EVEN / bed-night   {result['break_even_per_bed_night']:>14,.2f}")

    if args.grid:
        print("\nScenario grid")
        print(scenario_grid(costs, bookings).to_string(index=False))


if __name__ == "__main__":
    main()
