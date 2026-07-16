# Healthcare Revenue & Operations Analytics

Independent project analyzing a 72,000-encounter healthcare billing dataset to quantify
revenue leakage, denial patterns, and department-level collection performance —
built to practice and demonstrate real revenue-cycle analytics using SQL, Python, and Power BI.

**Live dashboard:** see `/dashboard/index.html` (open directly in a browser) or the hosted
version linked from my [portfolio site](../../index.html).

## Key findings

| Metric | Value |
|---|---|
| Total encounters | 72,000 |
| Total billed revenue | Rs. 11.25 Cr |
| Total collected revenue | Rs. 8.11 Cr |
| Revenue leakage | 27.9% |
| Overall denial rate | 10.1% |
| Highest-denial payer | Medicaid (13.7%) |
| Top denial driver (by revenue at risk) | Coverage Terminated (Rs. 0.15 Cr) |

## Dataset

`data/healthcare_encounters.csv` — synthetically generated (see `python/generate_data.py`)
to mirror realistic healthcare revenue-cycle patterns: department-level billing variance,
payer-specific denial rate differences, and a mix of Paid / Denied / Partially Paid / Pending
claim statuses. Not real patient data — built for portfolio/learning purposes.

Columns: `encounter_id`, `patient_id`, `department`, `payer`, `service_date`, `billed_amount`,
`allowed_amount`, `paid_amount`, `claim_status`, `denial_reason`.

## Repo structure

```
├── data/
│   └── healthcare_encounters.csv       # 72,000-row synthetic dataset
├── sql/
│   └── revenue_cycle_analysis.sql      # 6 analysis queries: leakage, denial rate,
│                                         root cause, contribution margin, trend, recovery sizing
├── python/
│   ├── generate_data.py                # Synthetic data generator
│   └── analysis.py                     # pandas reproduction + matplotlib charts
├── dashboard/
│   ├── index.html                      # Interactive HTML dashboard (Chart.js)
│   └── assets/                         # Static chart PNGs + KPI JSON
├── POWER_BI_GUIDE.md                   # DAX measures + report build guide
└── README.md
```

## Methods

- **SQL** (SQLite): multi-table joins, subqueries, and aggregate functions to compute
  revenue leakage, payer-level denial rates, root-cause revenue impact ranking,
  department contribution margins, monthly trend, and a benchmark-based recovery
  opportunity estimate.
- **Python**: pandas for analysis validation, matplotlib for static charts.
- **Power BI**: DAX measures for the same metrics, built following `POWER_BI_GUIDE.md`.

## Reproduce it yourself

```bash
pip install pandas numpy matplotlib
python python/generate_data.py     # regenerates data/healthcare_encounters.csv
python python/analysis.py          # regenerates charts + dashboard/assets/kpi_data.json
```

Then open `sql/revenue_cycle_analysis.sql` against the generated CSV (loaded into SQLite
or any SQL engine) to run the analysis queries directly.

## Author

Dev Sahni — [LinkedIn](https://www.linkedin.com/in/dev-sahni-39595131a) · [Portfolio](https://devsahni03.github.io) · devsahni03@gmail.com
