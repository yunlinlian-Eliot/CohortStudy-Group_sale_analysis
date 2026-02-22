# CohortStudy-Group_sale_analysis
**📌 Project Overview**
Cohort-based repeat purchase analysis to evaluate customer retention and spending behavior across 6/12/15-month windows.

**🎯 Business Objectives**
Define "Repeat Customer": Establish a rigorous definition of repeat behavior (distinguishing casual users from regular customers).

Time-Window Retention: Measure conversion rates for second purchases within 6, 12, and 15-month windows.

Spending Analysis: Compare the monetary value of the repeat purchase against the first purchase to determine if customer "value" is increasing or decreasing.

**🛠 Tech Stack**
Language: Python (Pandas, NumPy)
Data Processing: SQL (Data extraction & cleaning)
Methodology: Cohort Analysis, Time-Series Filtering

**🧠 Data Logic & Methodology (The "Professional" Part)**
To ensure the analysis was unbiased and statistically significant, I implemented the following logic:

1. Observation Buffer (The 15-Month Rule)
Data Range: Full dataset spans Jan 2021 – Dec 2025.

Lead Identification: Only customers whose First Purchase occurred between Jan 2021 and Sep 2024 were included.

Rationale: This ensures every customer in the study has at least a 15-month window (up to Dec 2025) to demonstrate repeat behavior, preventing "right-censoring" bias where newer customers appear as non-repeaters simply due to lack of time.

2. Data Cleaning & Granularity
Unit of Analysis: "Unique-date, Unique-customer" total bill amount (excluding GST).

Frequency Logic: Multiple transactions on the same day are treated as a single "Visit/Purchase" to avoid skewing frequency metrics.

Windowing: Calculated 3 distinct tracking periods (6m, 12m, 15m) from each individual's First_Purchase_Date.

**📈 Key Metrics Tracked**
Retention Rate (%): Percentage of unique headcounts who made a 2nd purchase within the specific window.

Purchase Amount Variance:
% Amount Increased: Customers spending more on their repeat visit.
% Amount Decreased: Customers spending less (potential signal of declining brand attraction).

**💡 Key Contributions & Skills**
Data Pipeline Construction: Developed a script to automate the "First Purchase" identification and window-based filtering.

Business Insight: Translated ambiguous stakeholder requirements (from "visits" vs "purchases") into a concrete technical schema.

Complex Problem Solving: Handled overlapping time windows and ensured mutually exclusive denominator logic for percentage calculations.
