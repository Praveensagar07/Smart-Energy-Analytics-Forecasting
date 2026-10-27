# Big Data & Machine Learning Methodology

## Smart Energy Consumption Analytics & Forecasting
**Academic Batch**: 13  
**Authors**: Praveen Sagar.M & Naveen.S

---

## 1. Mathematical Formulation & Physical Units

Smart meter datasets measure instantaneous power demand, which must be mathematically integrated over time to compute energy consumption in standard billing units (kilowatt-hours, kWh).

### A. Interval Energy Formulation
For an active power measurement $P_t$ recorded in kilowatts (kW) at 1-minute sampling intervals $\Delta t = 1 \text{ min} = \frac{1}{60} \text{ hours}$:
$$\text{Energy}_t (\text{kWh}) = P_t \times \Delta t = P_t \times \frac{1}{60}$$

### B. Daily Energy Aggregation
For day $d$ spanning $N_d$ valid minute readings:
$$E_{\text{daily}, d} = \sum_{t=1}^{N_d} \left( \frac{P_{t, d}}{60} \right)$$
For a complete 24-hour day, $N_d = 1440$ readings. The daily completeness ratio is defined as:
$$C_d = \frac{N_d}{1440}$$
A day is deemed representative for historical baseline and predictive modeling if $C_d \ge 0.85$ (at least 1,224 valid minutes).

### C. Sub-Metering Disaggregation
Sub-meters $S_1, S_2, S_3$ record energy in Watt-hours (Wh). They are normalized to kWh via:
$$S_{i, \text{kWh}} = \frac{S_{i, \text{Wh}}}{1000}$$
The unmetered remainder energy representing unmonitored circuits (lighting, electronics, secondary plugs) is computed as:
$$S_{\text{remainder}} = \max\left(0, E_{\text{daily}} - \sum_{i=1}^3 S_{i, \text{kWh}}\right)$$

---

## 2. Feature Engineering & Strict Leakage Prevention

In time-series forecasting, data leakage occurs when future or contemporaneous information is inadvertently leaked into predictor features. To guarantee causality:

### A. Lagged Predictors
Predictor features for target day $t$ strictly reference prior calendar dates:
- $\text{Lag}_1(t) = E_{t-1}$ (Previous day consumption)
- $\text{Lag}_2(t) = E_{t-2}$
- $\text{Lag}_7(t) = E_{t-7}$ (Same day of prior week, capturing 7-day cyclical seasonality)

### B. Preceding Rolling Windows
Rolling statistical features over window $W \in \{7, 14\}$ days are calculated strictly on preceding days:
$$\mu_{W}(t) = \frac{1}{W} \sum_{k=1}^W E_{t-k}$$
$$\sigma_{W}(t) = \sqrt{\frac{1}{W-1} \sum_{k=1}^W (E_{t-k} - \mu_W(t))^2}$$
In PySpark SQL Window syntax, this is enforced through:
```python
Window.orderBy("Date_ISO").rowsBetween(-W, -1)
```
This guarantees that day $t$'s actual consumption $E_t$ is excluded from the rolling mean.

---

## 3. Chronological Model Evaluation

### A. Non-Shuffled Partitioning
Standard k-fold cross-validation randomly shuffles observations, which violates temporal independence and leads to artificially inflated accuracy metrics. This project implements a strict sequential chronological split:
- **Training Set (70%)**: December 24, 2006 to September 14, 2009 ($N_{\text{train}} = 989$ days)
- **Validation Set (15%)**: September 15, 2009 to April 18, 2010 ($N_{\text{val}} = 211$ days)
- **Held-Out Test Set (15%)**: April 19, 2010 to November 26, 2010 ($N_{\text{test}} = 213$ days)

Model hyperparameters were tuned on the validation set, and final generalization capability was evaluated on the untouched test period.

### B. Evaluation Metrics
For actual values $y_i$ and predicted values $\hat{y}_i$ across $N$ test days:
1. **Mean Absolute Error (MAE)**:
   $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |y_i - \hat{y}_i|$$
2. **Root Mean Squared Error (RMSE)**:
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2}$$
3. **Coefficient of Determination ($R^2$)**:
   $$R^2 = 1 - \frac{\sum_{i=1}^N (y_i - \hat{y}_i)^2}{\sum_{i=1}^N (y_i - \bar{y})^2}$$
4. **Mean Absolute Percentage Error (MAPE)**:
   $$\text{MAPE} = \frac{1}{N} \sum_{i=1, y_i > 0.5}^N \left| \frac{y_i - \hat{y}_i}{y_i} \right| \times 100\%$$

---

## 4. SDG 7 Alignment: Affordable & Clean Energy

The analytical and predictive pipelines directly address United Nations Sustainable Development Goal 7 (Target 7.3: Double the global rate of improvement in energy efficiency):
1. **Intra-Day Peak Shaving**: Identifies the 18:00–21:00 evening peak where household demand averages 2.12 kW, exerting maximum stress on the electrical grid.
2. **Nocturnal Load Shifting**: Demonstrates that shifting heavy discretionary thermal loads (laundry, dishwashing, water heating) to the 01:00–05:00 valley (averaging 0.48 kW) lowers grid peak-to-average ratio (PAR) and saves residential consumers €280–€420 annually under time-of-use tariffs.
3. **Statistical Anomaly Detection**: Automatically flags anomalous consumption spikes ($> \mu + 2\sigma = 48.2 \text{ kWh}$), enabling prompt identification of malfunctioning appliances, continuous parasitic baseloads, or thermal insulation leakage.
