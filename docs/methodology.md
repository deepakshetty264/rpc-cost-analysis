# Cost Model — Methodology

How the cost model is constructed, and why. No client figures appear here; the worked examples use illustrative numbers.

---

## Core principle

Three properties of each cost line are decided **separately** and resolved in a fixed order. Conflating them is the most common source of error in this kind of model.

| Decision | Question | Field |
|---|---|---|
| **Timing** | Charge the whole cost this year, or spread it? | `is_capital` |
| **Scope** | Does this cost belong in the pricing base at all? | `affects_pricing` |
| **Behaviour** | Does the cost scale with activity? | `cost_category` |

---

## Step 1 — Timing

Operating costs pass through as annual figures. Capital items are spread over useful life using straight-line depreciation, with salvage treated as zero (appropriate for equipment with negligible resale value).

```
annual_cost = value / useful_life  if capital else value
```

Three modes are supported so the effect of the choice is visible rather than assumed:

| Mode | Rule | Answers |
|---|---|---|
| `full` | charged in full this year | impact if assets are self-funded from current income |
| `depreciate` | spread over useful life (default) | steady-state annual cost of holding the asset base |
| `exclude` | removed entirely | operating cost where capital is funded separately |

Useful lives can be set per asset class (vehicles, boats, safety equipment, general kit) or as a single blanket figure. Where capital is a small share of total cost, the choice has negligible effect on the headline result — worth demonstrating rather than assuming.

**Scope boundary.** Only assets on the operating entity's own budget belong in the model. Infrastructure funded by a parent organisation's estates function is excluded, because it is not a cost the entity can recover through pricing.

---

## Step 2 — Scope

A flag determines whether a cost belongs in the base that pricing is expected to recover.

| Mode | Rule | Answers |
|---|---|---|
| `all` | every line included | full cost recovery |
| `pricing_only` | flagged lines only | cost of service delivery |

The gap between the two is itself a finding: it quantifies how much cost sits outside what pricing currently covers.

**Interaction to watch.** A capital item excluded under `pricing_only` has its depreciation recovered nowhere. That is only correct if the asset is genuinely funded outside operating income.

---

## Step 3 — Behaviour

The test: does the cost change with activity volume within the operating range?

- **Fixed** — incurred regardless of volume (salaried establishment, standing utility charges, site upkeep, licences, equipment)
- **Variable** — scales with participants or sessions (food, consumables, participant-linked utilities, casual staffing)

### Testing the classification

Where sufficient periodic data exists, the high–low method can be used to test whether a line behaves as assumed. In practice this often **fails informatively**: a cost with high off-season consumption (heating an unoccupied building) can produce a negative implied variable rate. That is not a reason to discard the method — it is evidence the cost is not activity-driven, and supports a conservative fixed classification.

### Staffing

Where a salaried establishment is paid year-round regardless of occupancy, it is fixed by definition, irrespective of whether individual roles are delivery-facing. Casual or bought-in staffing is the genuinely variable element.

A role-band breakdown of the salaried figure is useful descriptively, but does not move anything between pools. Do not model below the granularity the client can actually supply.

---

## Step 4 — Volume base

**Bed-nights** (participants × nights) are the recommended activity driver for a residential operation: they capture headcount and duration together, where either alone distorts.

| Base | Used for |
|---|---|
| all bed-nights | variable costs, always |
| all bed-nights | fixed costs — recognises all occupancy as genuine utilisation |
| chargeable only | fixed costs — attributes them to commercial activity only |

The fixed-cost base is a genuine choice with a material effect. Report both.

---

## Step 5 — Break-even

```
variable_per_bed_night   = variable_pool / total_bed_nights
fixed_per_bed_night      = fixed_pool    / allocation_base
break_even_per_bed_night = fixed_per_bed_night + variable_per_bed_night
```

### Comparing to price — the critical rule

Normalise **both sides** to the same unit before drawing any conclusion.

A per-course list price assumes a standard course size. Comparing that fixed price against the full cost of a much larger or longer course makes every oversized booking appear underpriced as an artefact of the mismatch. Establish what standard size each tariff assumes, then compare per bed-night:

```
recovery = list_price_per_bed_night / break_even_per_bed_night
```

### Product-level caution

A single blended rate spreads all costs evenly across all bed-nights. That is valid for a centre-wide break-even, but **not** for claims about individual product lines — a self-catered product carries a share of catering cost it never consumed. Per-product claims require per-product allocation, and are unreliable where a product has very few observations.

---

## Occupied versus unoccupied daily cost

The fixed/variable split answers a question operators frequently ask directly:

```
unoccupied_day = fixed_pool / 365                    # cost of simply existing
occupied_day   = unoccupied_day + (variable_pool / occupied_days)
```

Use distinct occupied dates, not bed-nights, for this view.

---

## Incremental versus fully loaded

For a discrete programme within a larger operation, two figures answer different questions:

| Basis | Includes | Answers |
|---|---|---|
| Incremental | only costs the programme caused | does it cover its own costs? |
| Fully loaded | plus a share of standing overhead | does it cover its fair share? |

Both are legitimate. Reporting only the incremental figure overstates profitability; reporting only the fully loaded figure can make a genuinely contributing programme appear to fail. Negative results on a fully loaded basis for small, short instances are usually **allocation artefacts rather than cash losses** — a low-occupancy week carrying a full period's fixed staffing. Say so explicitly.

---

## Scenario grid

The three switches are independent, producing a grid rather than a single answer:

| Switch | Options |
|---|---|
| capital_treatment | full / depreciate / exclude |
| cost_scope | all / pricing_only |
| fixed_allocation | all / chargeable |

Recommended base case: `depreciate` + `all` + `all`. Then vary one at a time to isolate each effect. **Presenting the grid rather than a point estimate is the point** — it shows how sensitive the answer is to assumptions that are judgements rather than facts.

---

## Data governance notes

Two practices that proved necessary:

**Versioned datasets with a decision log.** Every cleaning transformation recorded, distinguishing mechanical corrections from analytical judgements and from values that could not be verified. This makes the analysis auditable and surfaces the assumptions that a reader is entitled to challenge.

**Control-total reconciliation.** Reconcile the cleaned dataset back to the client's own management accounts before analysing. Discrepancies found at this stage are cheap; discrepancies found after the analysis is built are not.

**Peer verification of foundational files.** Where one dataset underpins everything downstream, a second person should verify it independently. An error in a foundation file propagates silently through every subsequent result.
