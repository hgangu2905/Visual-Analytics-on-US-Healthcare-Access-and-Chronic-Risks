# The Cost of Chronic Illness: How Preventable Health Risks Drive Medicare Inpatient & Post‑Acute Costs (Tableau Story)

A real‑world public–health analytics project that merges **CMS** utilization & payments with **CDC BRFSS** risk factors and **KFF** insurance coverage to tell a prevention‑first story in **Tableau**.

---

## 🎯 Problem Statement

**How do preventable chronic health risks and access gaps influence Medicare’s inpatient and post‑acute (Skilled Nursing Facility) costs across U.S. states?**  
We examine whether states with higher prevalence of conditions and behaviors like **diabetes, obesity, hypertension, smoking, and physical inactivity** also show **higher Medicare inpatient spending and SNF burden**, and how **insurance coverage** relates to these costs.

---

## 📊 Datasets (Public & Real‑World)

**Core (CMS):**
- **CMS #2 – Medicare Inpatient Hospitals by Geography & Service** (state‑level discharges, payments, DRGs, length‑of‑stay).  
- **CMS #8 – Medicare Skilled Nursing Facility (SNF) — Program Statistics** (state‑level covered stays, days of care, total program payments).

**Drivers & Context:**
- **CDC BRFSS – Age‑Adjusted Prevalence** (state‑year estimates for obesity, diabetes, hypertension, smoking, physical inactivity, etc.).
- **KFF – Health Insurance Coverage of the Total Population** (state‑year uninsured %, plus employer/Medicaid/Medicare mix).

> All sources are official portals (CMS, CDC, KFF). Downloaded in their native CSV/XLS formats, then standardized for merging.

---

## 🗺️ Scope & Grain

- **Unit of analysis:** U.S. **state × year**.  
- **Time windows (typical):** BRFSS (2011–present), KFF (2008–2023), CMS SNF (2017–2021 window used), CMS Inpatient (multi‑year by state).  
- **Join keys:** `State` (or FIPS where available), `Year`.

---

## 🧹 Data Preparation (Python/Spreadsheet‑friendly)

1. **Standardize field names** (snake_case) and state codes (use USPS abbreviations where available).  
2. **Filter relevant years** so all sources overlap (e.g., 2017–2021 for the SNF window).  
3. **Clean types & units:** strip `%`, cast numerics, unify `year` to integer.  
4. **Select BRFSS indicators** (e.g., obesity, diabetes, hypertension, smoking, inactivity). Keep `estimate_pct` per state‑year.  
5. **Select KFF coverage fields**: uninsured %, and optionally coverage mix (employer/Medicaid/Medicare).  
6. **Extract CMS metrics:**  
   - Inpatient: total Medicare spend/payment, discharges, and optional DRG views.  
   - SNF: total program payments, covered admissions, covered days of care.  
7. **Merge** on `state, year` to build a single **analysis‑ready table** for Tableau.  
8. **Optional derived fields:** cost per beneficiary, SNF days per admission, z‑scores (to compare across metrics).

> Repository suggests `data/raw/` for original files and `data/processed/` for the merged dataset used in Tableau.

---

## 🧠 KPIs & Calculations (used in Tableau)

- **Total Inpatient Spend (State-Year)** – from CMS #2.  
- **SNF Total Program Payments (State-Year)** – from CMS #8.  
- **BRFSS Risk (%), by Topic** – e.g., diabetes %, obesity %, inactivity %.  
- **Uninsured % (State-Year)** – from KFF.  
- **YoY % Change** (generic):  
  ```
  (SUM([Measure]) - LOOKUP(SUM([Measure]), -1)) 
  / ABS(LOOKUP(SUM([Measure]), -1))
  ```
  *Put `Year` on Columns as Discrete; Table Calculation across Year.*

---

## 🖥️ Dashboards (v1 shipped)

### 1) **Overview (Landing)**
**Purpose:** Fast context of access & cost hotspots.  
**Elements:**  
- KPI tiles: *Highest Uninsured (latest), Highest Inpatient Spend, Highest SNF Spend*.  
- US map toggle for a key KPI.  
- 2–3 lines of narrative explaining the problem statement.

### 2) **Access & Coverage**
**Question:** *Where are coverage gaps and what’s the coverage mix?*  
**Sheets:**  
- **Uninsured by State (Map)** — color by uninsured %, filter by Year.  
- **Coverage Breakdown (Bar)** — employer/Medicaid/Medicare/uninsured for the selected state.

### 3) **Inpatient & Post‑Acute Cost**
**Question:** *Which states are cost hotspots across the care pathway?*  
**Sheets:**  
- **Inpatient Total Medicare Spend (Bar by State)**.  
- **SNF Total Program Payments (Bar/Map by State)**.  
**Interaction:** Selecting a state highlights both visuals.

### 4) **Health Risks → Costs**
**Question:** *Do higher risk factors align with higher costs?*  
**Sheets:**  
- **Risk Trend (Line)** — choose Topic (Diabetes/Obesity/Inactivity); filter by State.  
- **Risk vs Cost (Scatter)** — BRFSS estimate (%) vs Inpatient Spend or SNF Payments; add trendline.  
**Insight hook:** Try different risk topics to see which aligns most with cost.

---

## 🗂️ Suggested Repo Structure

```
healthcare-risk-costs-tableau/
├── data/
│   ├── raw/
│   │   ├── cms_inpatient.csv
│   │   ├── cms_snf_2017.xlsx
│   │   ├── cms_snf_2018.xlsx
│   │   ├── cms_snf_2019.xlsx
│   │   ├── cms_snf_2020.xlsx
│   │   └── cms_snf_2021.xlsx
│   └── processed/
│       └── merged_state_year.csv
├── notebooks/  # optional: preprocessing
│   └── preprocess_and_merge.ipynb
├── tableau/
│   └── dashboard.twbx  # or link to Tableau Public
├── README.md
└── LICENSE
```

---

## 🔁 Interactivity & UX

- **Global Year filter** across dashboards.  
- **State selection** (click map/bar) to drive details.  
- **Highlight actions** to connect inpatient & SNF views.  
- **Tooltips** with formatted numbers and fallback text (`IFNULL`) where data is missing.

---

## ✅ What This Project Demonstrates

- End‑to‑end **public‑data integration** (CMS + CDC + KFF).  
- **Cleaning, merging, and modeling** data to answer a **policy‑relevant question**.  
- **Tableau storytelling** with multiple dashboards that move from **problem → drivers → implications**.  
- A defensible, prevention‑focused narrative suitable for **resumes, interviews, and portfolios**.

---

## 🧭 Future Work (planned next)

- **Drilldowns**: per‑DRG inpatient cost drivers; SNF length‑of‑stay vs payments.  
- **Normalization**: add Census 65+ population to compute per‑beneficiary signals.  
- **Equity layers**: rural/urban, HPSA, income/education overlays.  
- **Preventable hospitalizations**: add HHS/CDC indicators to estimate avoidable cost.  
- **Scenario view**: simple projections if risk factors improve by X%.

---

## 📌 How to Reproduce

1. **Download raw data** from CMS, CDC BRFSS, KFF (links listed above).  
2. **Place files in** `data/raw/` and **run** your cleaning/merge (Python or spreadsheet).  
3. **Export** `merged_state_year.csv` to `data/processed/`.  
4. **Open Tableau**, connect to the processed file and the raw tables as needed.  
5. **Recreate sheets** listed above and assemble the four dashboards.  
6. **Publish** to Tableau Public (include the link in this README).

---

## 📄 License & Attribution

- All data © their respective providers (CMS, CDC, KFF).  
- This repository’s code and workbook: MIT (or as you prefer).  
- Please credit the sources if you reuse this work.

