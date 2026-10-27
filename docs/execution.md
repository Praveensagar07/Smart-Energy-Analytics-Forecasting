# Pipeline Execution & Demonstration Guide

## Smart Energy Consumption Analytics & Forecasting
**Academic Batch**: 13  
**Authors**: Praveen Sagar.M & Naveen.S

---

## 1. Quick Start: Master Automated Runner

To sequentially execute and verify all project phases in a single automated workflow:

```powershell
python scripts/run_pipeline.py
```

This single command triggers:
1. Ingestion and data cleaning (`clean_data.py`)
2. Hadoop MapReduce streaming aggregation and mathematical validation (`run_mapreduce.py`)
3. HiveQL analytical query execution (`run_hive_analytics.py`)
4. PySpark time-series feature engineering (`spark_feature_pipeline.py`)
5. Spark MLlib forecasting model training and evaluation (`train_models.py`)
6. Power BI star-schema export generation (`generate_dashboard_exports.py`)
7. Publication figure rendering (`generate_plots.py`)
8. Complete test suite verification (`pytest tests/ -v`)

---

## 2. Step-by-Step Module Execution

### Phase 1: Data Preprocessing & Validation
Reads raw one-minute measurements (2,075,259 records), converts kW to kWh ($P \times 1/60$), converts Wh to kWh ($/1000$), computes unmetered remainder, tracks daily completeness, and outputs hourly/daily summaries:
```powershell
python preprocessing/clean_data.py --input-file data/raw/household_power_consumption.txt
```
*Outputs*:
- `data/processed/daily_energy_consumption.csv` (1,433 rows)
- `data/processed/hourly_energy_consumption.csv` (34,168 rows)
- `data/processed/cleaning_summary.json`

### Phase 2: Hadoop MapReduce Execution
Executes the MapReduce streaming pipeline (Mapper $\rightarrow$ Partition/Sort $\rightarrow$ Reducer) and automatically compares the aggregated daily energy against an independent Pandas reference:
```powershell
python hadoop/run_mapreduce.py
```
*Outputs*:
- `hadoop/mapreduce_daily_output.txt`
- Console verification log demonstrating $< 0.0001$ kWh difference.

For real Hadoop cluster / WSL submission:
```bash
bash hadoop/run_hadoop_job.sh
```

### Phase 3: HiveQL Analytical Queries
Executes all 8 HiveQL queries using Apache Spark's Hive-compatible SQL engine:
```powershell
python hive/run_hive_analytics.py
```
*Outputs*:
- `hive/query_results/q1_daily_consumption.csv` ... `q8_submetering_breakdown.csv`
- `hive/hive_execution_report.md`

### Phase 4: PySpark Feature Engineering
Builds leak-free chronological historical lags and rolling statistical windows using PySpark Windowing:
```powershell
python spark/spark_feature_pipeline.py
```
*Outputs*:
- `data/features/daily_energy_features.csv` (1,413 complete chronological records, 18 features)

### Phase 5: Machine Learning Forecasting
Trains and validates the Naive Baseline, Spark MLlib Linear Regression, and Spark MLlib Random Forest Regressor on strict chronological partitions:
```powershell
python forecasting/train_models.py
```
*Outputs*:
- `forecasting/test_predictions.csv` (213 test days actual vs predicted)
- `forecasting/evaluation_metrics.json`

### Phase 6: Power BI Exports & Publication Figures
Generates the Star-Schema CSV exports and renders publication-ready plots:
```powershell
python dashboard/generate_dashboard_exports.py
python dashboard/generate_plots.py
```
*Outputs*:
- `dashboard/power_bi_exports/*.csv` (5 tables)
- `screenshots/01_energy_overview.png`
- `screenshots/02_consumption_analysis.png`
- `screenshots/03_forecasting_results.png`
- `screenshots/04_sustainability_insights.png`

---

## 3. Running Automated Tests

Run the full automated test suite covering all 24 unit tests:
```powershell
python -m pytest tests -v
```

Run specific test modules:
```powershell
pytest tests/test_preprocessing.py -v
pytest tests/test_mapreduce.py -v
pytest tests/test_features.py -v
pytest tests/test_models.py -v
pytest tests/test_dashboard_exports.py -v
```

---

## 4. Evaluation Demonstration Sequence for College Viva

When presenting to academic evaluators, execute the demonstration in this sequence:
1. **Show Environment Diagnostics**:
   ```powershell
   python scripts/verify_environment.py
   ```
2. **Show Unit Test Pass Rate**:
   ```powershell
   pytest tests -v
   ```
   *(Demonstrates 24/24 tests passing with zero failures).*
3. **Show MapReduce Mathematical Equivalence**:
   ```powershell
   python hadoop/run_mapreduce.py
   ```
   *(Demonstrates mapper, reducer, and $< 0.0001$ kWh agreement with independent reference).*
4. **Show HiveQL Query Execution & Report**:
   Display `hive/hive_execution_report.md` and query results in `hive/query_results/`.
5. **Show Machine Learning Predictions & Evaluation Metrics**:
   Display `forecasting/evaluation_metrics.json` and `forecasting/test_predictions.csv`.
6. **Show Dashboard Visualizations**:
   Open images in `screenshots/` and Power BI data model in `dashboard/dashboard_layout.md`.
