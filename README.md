# Cost Analysis and Pricing Model — Outdoor Education Centre

MSc Business Analytics capstone project, University of Birmingham (2026).

A cost and pricing analysis for a university-owned outdoor education centre, carried out by a five-person team over three months. This repository contains the **methodology, analysis code and reusable tooling** developed during the project.

> **Note on data.** All client data is confidential and is not included in this repository. The code is structured to run against the schema described in `docs/`, and the workbook template is supplied blank. Figures in any documentation here are illustrative.

---

## What the project addressed

The centre operates a mix of instructed courses, self-catered bookings and a summer recreation programme, and needed to understand:

1. Where its costs actually sat, and which behaved as fixed versus variable
2. What it costs to run the centre per day, occupied versus unoccupied
3. Whether current pricing recovered those costs
4. Where income could be improved

A significant part of the work was upstream of the analysis: reconstructing a usable dataset from records held across multiple spreadsheets and formats.

---

## Approach

| Stage | Method |
|---|---|
| Cost classification | Cost behaviour analysis; fixed/variable split tested against activity |
| Capital treatment | Straight-line depreciation, with per-asset-class useful lives |
| Unit costing | Activity-based costing principles; bed-nights as the activity driver |
| Break-even | Cost–volume–profit analysis, per bed-night and per product line |
| Benchmarking | Comparison against a published rate card from a comparable centre |
| Scenario testing | Toggle-driven sensitivity across capital treatment, cost scope and allocation base |

The model is built so that the main modelling judgements — how capital is treated, whether all costs or only pricing-relevant costs are included, and which volume base fixed costs are spread over — are **configuration switches rather than hard-coded assumptions**, so their effect on the result can be shown rather than assumed.

---

## Repository structure

```
├── src/            Analysis scripts (Python)
├── templates/      Blank Excel workbook for ongoing record keeping
├── docs/           Methodology and cost-model logic specification
├── notebooks/      Exploratory analysis
└── data/           Not tracked — see below
```

---

## The record-keeping workbook

`templates/` contains a blank version of the Excel workbook built as a project deliverable. It is a single file with linked sheets covering bookings, staffing, costs and reference rates, plus a dashboard that summarises by financial year.

Features:
- Auto-calculated nights, bed-nights, invoiced value and outstanding balance
- Price lookup from an editable rate table, including banded and per-head tariffs
- Cost entries classified automatically from a reference list
- Dashboard driven by a single financial-year selector

It is supplied empty so it can be adapted to any similar operation.

---

## Running the analysis

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/cost_model.py
```

Place input files in `data/` following the schema in `docs/data_schema.md`. That directory is gitignored.

---

## Tools

Python (pandas, numpy, openpyxl) · Excel · Tableau

---

## Acknowledgements

Delivered with a team of five as part of the MSc Business Analytics programme at Birmingham Business School, with thanks to the centre's management team and to our academic supervisor.

## Licence

Code released under the MIT Licence. The methodology documentation is shared for reference; client data is excluded and remains confidential.
