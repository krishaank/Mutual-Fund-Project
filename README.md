# Bluestock Mutual Fund Analytics Capstone

Welcome to the Bluestock Mutual Fund Analytics project. This repository contains a fully automated end-to-end data engineering, analytics, and Business Intelligence platform built for analyzing 40 mutual fund schemes over a 3-year period (2022-2025).

## 🚀 Project Overview

The project was executed across 7 distinct phases:
1. **Data Ingestion:** Cleaned 10 raw CSV datasets and orchestrated them into a centralized SQLite Star Schema Data Warehouse (`bluestock_mf.db`).
2. **Exploratory Data Analysis (EDA):** Automated Jupyter notebooks to uncover macro trends, such as the industry reaching ₹81 Lakh Crores in AUM and SIP inflows peaking at ₹31K Crores.
3. **Performance Analytics:** Decoupled manager skill (Alpha) from market correlation (Beta) using OLS regression against the Nifty 100 benchmark.
4. **Advanced Risk Analytics:** Computed deep tail-risk metrics including 95% Historical Value at Risk (VaR) and Expected Shortfall (CVaR).
5. **Behavioral Data Science:** Developed cohort tracking and a Churn Prediction algorithm to flag "at-risk" retail SIP investors.
6. **BI Dashboard:** Built an interactive, natively-Python Streamlit dashboard to replace legacy BI tools like Power BI.
7. **Automated Documentation:** Generated automated PDF reports and PowerPoint presentations directly from the analytical findings.

## 🛠 Setup Instructions

### Prerequisites
- Python 3.9+
- SQLite3

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/krishaank/Mutual-Fund-Project.git
   cd Mutual-Fund-Project
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\\venv\\Scripts\\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure libraries like `pandas`, `sqlite3`, `scipy`, `streamlit`, `plotly`, `fpdf2`, and `python-pptx` are installed).*

## ⚙️ How to Run the Pipeline

The entire ETL, EDA, and Advanced Analytics workflow has been streamlined into a single master execution script. 

To run the pipeline from scratch and regenerate all databases, CSV reports, and Jupyter Notebooks, simply run:
```bash
python run_pipeline.py
```

## 📊 How to Open the Dashboard

To launch the interactive Business Intelligence Dashboard:
```bash
streamlit run app.py
```
This will automatically open the dashboard in your default web browser (typically hosted on `localhost:8501`).

## 🤖 How to use the Fund Recommender

You can test the command-line Mutual Fund Recommendation Engine, which dynamically maps risk appetite to risk-adjusted Sharpe ratio algorithms:
```bash
python recommender.py --risk Moderate
```
*(Options: Low, Moderate, High)*

## 📂 Deliverables & Repository Structure
- `bluestock_mf.db`: The centralized SQLite Star Schema.
- `app.py`: The interactive Streamlit Dashboard.
- `notebooks/`: Contains the executed Jupyter Notebooks (`EDA.ipynb`, `Performance_Analytics.ipynb`, `Advanced_Analytics.ipynb`).
- `reports/`: Contains the final `Final_Report.pdf` and `Bluestock_MF_Presentation.pptx`.
- `run_pipeline.py`: Master execution script.

---
*Developed by Krishaank.*
