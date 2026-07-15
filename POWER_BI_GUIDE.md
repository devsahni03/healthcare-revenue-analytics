# Power BI Build Guide — Healthcare Revenue & Operations Analytics

This guide gets you from the raw CSV to a finished, presentable Power BI report.
Everything below is based on the real dataset in `/data/healthcare_encounters.csv`
(72,000 rows) so the numbers you see in Power BI will match the SQL/Python analysis exactly.

---

## 1. Load the data

1. Open Power BI Desktop → **Get Data → Text/CSV** → select `healthcare_encounters.csv`.
2. Click **Transform Data** (Power Query Editor) before loading, and fix types:
   - `service_date` → Date
   - `billed_amount`, `allowed_amount`, `paid_amount` → Decimal Number
   - Everything else → Text
3. In Power Query, add a calculated column `Month` = `Date.StartOfMonth([service_date])` — you'll use this for the trend chart instead of relying on auto date hierarchies (cleaner for DAX time intelligence).
4. Close & Apply.

## 2. Build a Denial Reasons reference table (optional but recommended)

Power BI handles a dedicated **Denial Reason** dimension table better than reusing the fact table column directly for slicers. In Power Query, reference the main query, keep only the `denial_reason` column, remove duplicates and blanks — name this table `DenialReasons`. Create a relationship: `encounters[denial_reason]` → `DenialReasons[denial_reason]` (many-to-one).

## 3. Core DAX measures

Create these in a new table (Modeling → New Table → name it `_Measures`, or just add them to `encounters`):

```DAX
Total Billed (Cr) =
DIVIDE(SUM(encounters[billed_amount]), 10000000)

Total Collected (Cr) =
DIVIDE(SUM(encounters[paid_amount]), 10000000)

Revenue Leakage (Cr) =
[Total Billed (Cr)] - [Total Collected (Cr)]

Revenue Leakage % =
DIVIDE([Revenue Leakage (Cr)], [Total Billed (Cr)])

Total Encounters =
COUNTROWS(encounters)

Denied Encounters =
CALCULATE(COUNTROWS(encounters), encounters[claim_status] = "Denied")

Denial Rate % =
DIVIDE([Denied Encounters], [Total Encounters])

Denied Revenue (Cr) =
DIVIDE(
    CALCULATE(SUM(encounters[billed_amount]), encounters[claim_status] = "Denied"),
    10000000
)

Collection Rate % =
DIVIDE([Total Collected (Cr)], [Total Billed (Cr)])

Best Payer Denial Rate % =
CALCULATE(
    MINX(
        VALUES(encounters[payer]),
        DIVIDE(
            CALCULATE(COUNTROWS(encounters), encounters[claim_status]="Denied"),
            CALCULATE(COUNTROWS(encounters))
        )
    )
)

Recoverable Revenue (Cr) =
VAR PayerDenialRate = [Denial Rate %]
VAR BestRate = [Best Payer Denial Rate %]
VAR Gap = MAX(PayerDenialRate - BestRate, 0)
RETURN
DIVIDE(Gap * SUM(encounters[billed_amount]), 10000000)
```

**Why these matter in an interview:** `Best Payer Denial Rate %` and `Recoverable Revenue (Cr)` both use `CALCULATE` with a virtual table iteration (`MINX`/`VALUES`) — this is a step above simple aggregation and is a good thing to be able to explain if asked "walk me through a DAX measure you're proud of."

## 4. Suggested report layout (2 pages)

**Page 1 — Executive Summary**
- KPI cards across the top: Total Encounters, Total Billed (Cr), Total Collected (Cr), Revenue Leakage %, Denial Rate %
- Bar chart: Denial Rate % by Payer (sorted descending)
- Line chart: Revenue Leakage % by Month
- Bar chart: Collection Rate % by Department

**Page 2 — Denial Deep Dive**
- Bar chart: Denied Revenue (Cr) by Denial Reason (sorted descending)
- Table: Payer, Total Billed (Cr), Denial Rate %, Recoverable Revenue (Cr) — sorted by Recoverable Revenue descending
- Slicers: Payer, Department, Date range

## 5. Formatting notes (so it looks intentional, not default)

- Use a consistent 2-color palette (e.g. navy `#1F3864` for primary bars, coral `#993C1D` for "risk/negative" metrics like leakage and denials) — matches the resume/portfolio branding.
- Turn off gridlines on bar charts (Format → Gridlines → off).
- Add data labels on bar charts showing the actual %/Cr value, not just axis ticks.
- Use a single sentence "insight" text box under each chart (e.g. "Medicaid has the highest denial rate at 13.7%") — this is what actually makes a Power BI report look senior, not just default visuals.

## 6. Export & publish

- File → Export → PDF (for a static screenshot version to embed in your portfolio alongside the interactive HTML dashboard)
- If you have a Power BI Pro/organizational license, Publish to Power BI Service and use "Publish to web" for a shareable public link — add that link next to the GitHub repo link on your portfolio site and resume.

---

Once you've built this, replace the placeholder GitHub/portfolio links with your real ones, and you can honestly say in interviews: "I designed the DAX measures and report layout myself in Power BI Desktop" — because at that point, you will have.
