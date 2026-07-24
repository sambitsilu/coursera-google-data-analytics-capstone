# Real Estate Investment Portfolio Performance Analysis
> **A Google Data Analytics Capstone Case Study**  
> **Prepared by:** Sambit  
> **Dataset:** 269 de-identified property investment deals (2009–2021)

---

## 1. Executive Summary

This case study follows the six phases of the data analysis process (**Ask, Prepare, Process, Analyze, Share, Act**) to transform an operational real estate investment tracking workbook into a decision-ready analytics asset. The source dataset contains 269 property deals tracked by a private investment fund from 2009 through 2021. All identifying details (fund identity, broker/partnership names, street addresses, specific vendor names) have been pseudonymized or removed, while preserving 100% of the underlying financial metrics and calculations.

The original operational workbook contained typical real-world data issues: multi-header layouts with embedded summary rows above the primary data table, Excel error strings (`#DIV/0!`, `#VALUE!`), inconsistent text casing across categorical variables, and duplicate helper columns used for cash-flow calculations[cite: 1]. 

### Key Portfolio Takeaways
* **Total Profit:** **$9.99M** realized across tracked deals with a **79.9% win rate** (share of deals returning positive profit)[cite: 1].
* **Geographic Trends:** **Nevada** and **California** drove the highest volume, whereas **Georgia** and **Arizona** delivered the highest average returns on smaller deal volumes[cite: 1].
* **Predictive Modeling Finding:** A predictive model built to evaluate whether a deal's profitability could be forecast solely using purchase-time variables achieved only marginal predictive power (cross-validated ROC AUC 0.54)[cite: 1]. This negative result reveals that portfolio profitability is heavily dictated by downstream execution factors (rehab management, broker execution, exit timing) rather than purchase-time fundamentals alone[cite: 1].

---

## 2. Ask

### Business Task
Fund principals require a repeatable framework to determine which markets, property types, brokers, and deal structures yield optimal risk-adjusted returns, as well as an assessment of whether prospective deal profitability can be flagged prior to capital commitment[cite: 1].

### Stakeholders
* **Fund Principals:** Seek portfolio-level performance metrics broken down by state, property type, and broker to guide future capital deployment[cite: 1].
* **Acquisitions Team:** Require early-stage indicators to evaluate prospective deal quality before committing funds[cite: 1].
* **Portfolio Reviewers / Hiring Managers:** Require an end-to-end analytics workflow spanning data cleaning, exploratory analysis, predictive modeling, and dashboard architecture[cite: 1].

---

## 3. Prepare

### Data Source & ROCCC Assessment
The primary transactional data originates from the `MAIN` tab of an internal Excel workbook (269 deal records × 64 raw columns)[cite: 1]. 

| ROCCC Criterion | Assessment |
| :--- | :--- |
| **Reliable** | First-party operational data entered directly by the investment fund[cite: 1]. |
| **Original** | Primary-source transactional deal records[cite: 1]. |
| **Comprehensive** | Covers acquisition through disposition for all tracked fund deals, including active holdings[cite: 1]. |
| **Current** | Spans 2009–2021 (noting lower volume from 2018 onward)[cite: 1]. |
| **Cited** | Internal operational dataset; structural details documented in the Appendix[cite: 1]. |

### Known Data Limitations
* Unstructured `NOTES` fields contained non-standardized narrative caveats (e.g., HOA litigation, price disputes) that could not be parsed algorithmically and were excluded from quantitative modeling[cite: 1].
* 57 deals remain listed and 4 are under contract; their figures represent projected rather than realized outcomes and are tagged via `deal_status`[cite: 1].
* The `square_footage` field was blank across all 269 records and was excluded from analysis[cite: 1].

---

## 4. Process — Cleaning & Transformation

Data cleaning was executed programmatically using **Python (`pandas` + `openpyxl`)** to ensure complete reproducibility[cite: 1].

### 4.1 Structural Extraction
* Excluded the top 5 summary rows and embedded "Filtered Totals" row, anchoring extraction strictly to the primary table header at row 8[cite: 1].
* Extracted 269 contiguous deal records (rows 9–277)[cite: 1].
* Removed 20 redundant internal XIRR cash-flow helper columns, keeping primary fields: `Purchase Date`, `Sold Date`, `Purchase Price`, and finalized summary IRR metrics[cite: 1].

### 4.2 Data Type & Error Cleanup
* Converted 12 error-prone columns containing Excel error strings (`#DIV/0!`, `#VALUE!`, `"N/A"`) into numeric floats, casting calculation errors to null values[cite: 1].
* Standardized categorical variables (`state`, `property_type`, `broker`, `seller_channel`) to uppercase to eliminate string fragmentation[cite: 1].
* Converted binary status markers (`Under Contract`, `Listed`) into boolean fields, synthesizing a consolidated `deal_status` field (`Sold` / `Listed` / `Under Contract`)[cite: 1].
* Identified 10 extreme IRR outliers exceeding 5,000% annualized (caused by rapid flips held between 1 and 12 days)[cite: 1]. These were preserved in `*_raw` columns for reporting integrity while working columns were capped to null to prevent skewing distribution averages[cite: 1].

### 4.3 Feature Engineering
* `holding_period_months`: Days on market converted to months ($\text{days} / 30.44$)[cite: 1].
* `profit_margin_pct`: Realized profit divided by total cost ($\text{actual\_profit} / \text{total\_cost}$)[cite: 1].
* `deal_status`: Categorical mapping based on disposition indicators and sales dates[cite: 1].

### 4.4 De-identification
* Street addresses removed and replaced with a unique identifier (`DEAL-001` … `DEAL-269`)[cite: 1].
* Broker names, internal partnership entities, and vendors mapped to consistent, 1:1 rank-ordered pseudonyms (e.g., `Broker_01`, `Partner_01`, `Vendor_01`)[cite: 1].
* Unstructured text notes dropped to prevent exposure of identifiable information[cite: 1].

The final cleaned output is structured as `real_estate_deals_clean.csv` (269 rows × 46 columns)[cite: 1].

---

## 5. Analyze

### 5.1 Portfolio Overview
Across all 269 tracked deals (208 Sold, 57 Listed, 4 Under Contract), total cumulative profit reached **$9,999,357** with a **median deal profit of $13,327** and a **79.9% win rate**[cite: 1].

* **Vintage Performance:** The portfolio experienced its peak realized profit during the 2011–2012 acquisition years following the post-2008 housing market correction[cite: 1]. Acquisition volume dropped significantly after 2015[cite: 1].

### 5.2 Performance by Market & Property Type
* **Market Concentration:** Nevada (51 deals, 26% avg straight ROI) and California (36 deals, 24% avg straight ROI) comprised the largest share of overall deal volume[cite: 1]. 
* **High-Yield Markets:** Georgia (27 deals, 92% avg straight ROI) and Arizona (12 deals, 195% avg straight ROI) generated significantly higher average returns on smaller total deal counts[cite: 1].
* **Asset Classes:** Single-Family Residential (SFR) accounted for the core volume (182 deals) with moderate returns[cite: 1]. Commercial (14 deals) and Land acquisitions (18 deals) demonstrated wider return variance but significantly higher median yields[cite: 1].

### 5.3 Holding Period Dynamics
* Holding period demonstrates a positive correlation with straight ROI ($r = 0.41$) but a negative correlation with annualized ROI ($r = -0.13$)[cite: 1]. 
* *Insight:* While longer holding periods generate higher total absolute profit dollars, shorter hold durations achieve superior capital efficiency on an annualized basis[cite: 1].

### 5.4 Broker Efficiency
* `Broker_01` generated the highest transaction count (39 deals) with a modest average ROI of 22%[cite: 1].
* `Broker_02` completed 19 deals but produced the highest total profit contribution ($2.67M total profit, 161% avg ROI), driven primarily by commercial and debt-note acquisitions[cite: 1]. Transaction volume alone does not directly correlate with total profit generated[cite: 1].

---

## 6. Predictive Modeling Analysis

Two machine learning models were developed using pre-purchase features exclusively (`purchase_price`, `rehab_budget`, `loan_amount`, `state`, `property_type`, `seller_channel`) to evaluate whether deal success could be predicted prior to capital deployment[cite: 1].

### 6.1 Regression Model (Profit Dollar Prediction)
* **Model:** Random Forest Regressor targeting `actual_profit`[cite: 1].
* **Result:** Out-of-sample $R^2 = -0.21$[cite: 1]. 
* **Conclusion:** The model failed to outperform a naive baseline mean prediction[cite: 1]. Absolute dollar returns are heavily skewed by extreme upper-tail outliers that cannot be modeled reliably from 269 rows using purchase-time variables alone[cite: 1].

### 6.2 Classification Model (Binary Profitability Prediction)
* **Model:** Class-balanced Random Forest Classifier targeting binary profitability ($\text{actual\_profit} > 0$)[cite: 1].
* **Result:** Cross-validated mean ROC AUC was **0.54 ± 0.03** (effectively equivalent to random baseline probability)[cite: 1].

```text
Feature Importance Ranking (Classifier)
----------------------------------------
1. rehab_and_interest       [====================] ~0.21
2. total_cost               [==================  ] ~0.17
3. purchase_price           [===============     ] ~0.15
4. loan_amount              [=========           ] ~0.09
5. purchase_year            [======              ] ~0.06
