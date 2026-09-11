# Data Schema

The analysis expects two CSV files in `data/` (gitignored). No client data is distributed with this repository; the schema below lets the model be run against any comparable operation.

---

## `costs.csv`

One row per cost line per financial year.

| Column | Type | Values | Notes |
|---|---|---|---|
| `item` | string | — | Unique identifier for the cost line |
| `value` | float | — | Annual spend, or purchase price for capital items |
| `cost_category` | string | `Fixed` / `Variable` | Behaviour relative to activity volume |
| `is_capital` | string | `Y` / `N` | Whether the line is a capital purchase |
| `affects_pricing` | string | `Y` / `N` | Whether pricing is expected to recover it |
| `date` | date | ISO | Optional; drives financial-year assignment |
| `notes` | string | — | Optional |

Example:

```csv
item,value,cost_category,is_capital,affects_pricing
electricity,40000.00,Variable,N,Y
salaried_staff,350000.00,Fixed,N,Y
casual_staff,45000.00,Variable,N,Y
food,35000.00,Variable,N,Y
minibus,24000.00,Fixed,Y,Y
site_maintenance,7500.00,Fixed,N,N
```

**Classification guidance.** See `docs/methodology.md`. In short: a cost is variable only if it changes with activity volume within the operating range. A salaried establishment paid year-round is fixed regardless of whether the roles are delivery-facing.

---

## `bookings.csv`

One row per booking or course.

| Column | Type | Values | Notes |
|---|---|---|---|
| `booking_id` | string | — | Unique identifier |
| `product` | string | — | Product line (e.g. instructed, self-catered, recreation) |
| `client_type` | string | — | Segment, if pricing varies by it |
| `start_date` | date | ISO | |
| `end_date` | date | ISO | |
| `people` | int | — | Headcount |
| `nights` | int | — | Derived from dates, or supplied |
| `is_chargeable` | string | `Y` / `N` | Optional; used by the `chargeable` allocation base |
| `invoiced` | float | — | Optional; needed for price-recovery comparison |

Example:

```csv
booking_id,product,client_type,start_date,end_date,people,nights,is_chargeable,invoiced
B001,instructed,internal,2026-03-02,2026-03-04,32,2,Y,6700
B002,self_catered,external,2026-03-09,2026-03-11,20,2,Y,5260
B003,recreation,unknown,2026-08-02,2026-08-08,45,6,Y,14895
```

Bed-nights are computed as `people × nights`.

---

## Optional: `rates.csv`

Where pricing is banded, supply the tariff so list prices can be looked up rather than hard-coded.

| Column | Type | Notes |
|---|---|---|
| `product` | string | |
| `client_type` | string | |
| `tier` | string | Headcount band, or a label for per-head tiers |
| `rate` | float | |
| `basis` | string | `per_night`, `per_course` or `per_head` |

The `basis` column matters. Mixing per-night and per-course tariffs without tracking which is which is the most common source of error when comparing price to cost — see the comparison rule in `docs/methodology.md`.

---

## Preparation notes

**Reconcile before analysing.** Check the cleaned cost file against the organisation's own management accounts and resolve differences first.

**Log cleaning decisions.** Distinguish mechanical corrections from analytical judgements and from values that could not be verified. The third category belongs in your limitations, not buried in the data.

**Verify foundational files independently.** Whichever dataset everything else derives from — usually the booking or occupancy file — should be checked by a second person. An error there propagates silently.
