# HASE v1.1-HYPER-HYPE: Crypto Market Volatility & Non-Linear Chaos Simulator

Welcome to **HASE v1.1-HYPER-HYPE**, a high-performance simulation pipeline designed to generate synthetic crypto-asset price series and analyze them using advanced statistical and information-theoretic metrics. 

Unlike traditional generators based on simple geometric Brownian motion, this framework captures the extreme, non-linear, and structural behavioral patterns unique to crypto-asset markets—ranging from high-frequency algorithmic noise to speculative FOMO bubbles and cascading margin liquidations.

---

## 📈 Market Volatility Models

The simulator generates time-series sequences based on five distinct market regimes, each governed by its own mathematical and behavioral rules:

1. **Crypto_Bull_Trend (Logarithmic Drift)**
   * *Concept:* Simulates a sustainable organic bull market.
   * *Mechanism:* Driven by a logarithmic upward drift combined with Gaussian random walks, representing diminishing but persistent buying momentum interspersed with natural healthy pullbacks.

2. **Crypto_Bear_Crash (Cascading Panic & Dead-Cat Bounces)**
   * *Concept:* Models a severe market capitulation.
   * *Mechanism:* Uses an accelerating negative drift (panic factor) that intensifies over time. It incorporates sudden exponential upward spikes ("dead-cat bounces") and simulates a 15% flash drop if certain thresholds are breached, replicating leveraged long liquidations.

3. **HFT_Market_Flat (Mean-Reverting Noise)**
   * *Concept:* Represents a low-volatility, sideways consolidation zone dominated by High-Frequency Trading (HFT) bots.
   * *Mechanism:* Governed by an Ornstein-Uhlenbeck-like mean reversion process. The price is continuously pulled back toward a baseline anchor point with micro-Gaussian noise.

4. **Whale_Pump_Chaos (Asymmetric Market Manipulation)**
   * *Concept:* Models systemic price manipulation by large market entities ("whales").
   * *Mechanism:* A three-phase sequence consisting of low-volatility accumulation, a sudden vertical pump driven by an asymmetric exponential distribution, and a brutal distribution/dump phase where assets are unloaded into retail liquidity.

5. **Crypto_Hyper_Hype_Chaos (Non-Linear Feedback & FOMO Dynamics)**
   * *Concept:* A highly non-linear dynamic system modeling speculative frenzy and retail hysteria.
   * *Mechanism:* Operates via coupled feedback loops where price change accelerates market sentiment (`hype_sentiment`), and heightened sentiment increases price velocity. It includes sinusoidal instability to simulate shifting narrative cycles and a catastrophic 60% crash trigger to emulate systemic margin-call cascades when the asset becomes unsustainably overbought.

---

## 📊 The 9 Analytical Metrics Explained

Every generated time-series is passed through a lightweight feature extractor. These metrics are specifically chosen to unmask the hidden mathematical thumbprints left behind by different market dynamics.

### 1. Metric 1: Length (`Метрика_1_Длина`)
* **What it measures:** The total number of observations in the sequence (fixed to `SEQ_LENGTH`).
* **Why it matters:** Establishes the sample size baseline for statistical variance and confidence intervals.

### 2. Metric 2: Mean Value (`Метрика_2_Среднее`)
* **What it measures:** The arithmetic average price of the sequence.
* **Why it matters:** Identifies the global price anchor for the specific execution slice.

### 3. Metric 3: Standard Deviation (`Метрика_3_Станд_Отклонение`)
* **What it measures:** The dispersion of prices relative to their mean.
* **Why it matters:** Serves as the primary indicator of historical volatility. High-hype and crash regimes display drastically higher standard deviation compared to HFT flat zones.

### 4. Metric 4: Minimum (`Метрика_4_Минимум`)
* **What it measures:** The absolute lowest price boundary observed in the sequence.
* **Why it matters:** Evaluates the maximum drawdown and checks for proximity to zero (bankruptcy/delisting emulation).

### 5. Metric 5: Maximum (`Метрика_5_Максимум`)
* **What it measures:** The peak price point achieved during the simulation run.
* **Why it matters:** Pinpoints the local ceiling, essential for measuring pump magnitudes and bubble peaks.

### 6. Metric 6: Transition Anomaly (`Метрика_6_Аномалия_Переходов`)
* **What it measures:** The ratio of the maximum absolute single-step price change to the mean absolute change:
  $$\text{Anomaly} = \frac{\max(|\Delta X_t|)}{\text{mean}(|\Delta X_t|)}$$
* **Why it matters:** Captures black swan events, flash crashes, and single-candle pumps. A high ratio indicates that the series is dominated by sudden jumps rather than smooth continuous adjustments.

### 7. Metric 7: Lag-1 Autocorrelation (`Метрика_7_Автокорреляция_Лаг1`)
* **What it measures:** The linear correlation between the price at time $t$ and the price at time $t-1$.
* **Why it matters:** Detects market memory. Organic trends display strong positive lag-1 autocorrelation (persistence), HFT flat markets show near-zero or negative autocorrelation (mean-reverting antipersistence), and hype phases show sudden structural breakdowns in autocorrelation stability.

### 8. Metric 8: Directional Sign Entropy (`Метрика_8_Энтропия_Направлений`)
* **What it measures:** The Shannon Entropy of the binary price movements (up versus down).
  $$H(X) = - (p_{\text{up}} \log_2 p_{\text{up}} + p_{\text{down}} \log_2 p_{\text{down}})$$
* **Why it matters:** Measures market directional symmetry and unpredictability. If a market moves up 50% of the time and down 50% of the time, entropy is maximized at $1.0$ (perfectly unpredictable random walk). Persistent bull/bear trends yield significantly lower entropy values due to directional bias.

### 9. Metric 9: Benford's Law Deviation Proxy (`Метрика_9_Прокси_Бенфорда`)
* **What it measures:** The sum-of-squared deviations between the empirical distribution of first significant digits in the sequence and the theoretical distribution predicted by Benford's Law:
  $$P(d) = \log_{10}\left(1 + \frac{1}{d}\right), \quad d \in \{1, \dots, 9\}$$
* **Why it matters:** Naturally occurring macro-economic data and geometric growth patterns adhere tightly to Benford's Law (where the digit 1 appears roughly 30.1% of the time). Artificial constraints, rigid range-bound algorithmic trading (HFT Flat), or forced modular arithmetic drastically warp this distribution, causing a massive spike in this deviation proxy.

---

## 📂 Dataset Architecture & Formatting

The engine outputs a highly structured, Excel-optimized `;`-delimited CSV file (`crypto_hype_chaos_dataset.csv`). 

To prevent Microsoft Excel from corrupting scientific strings (such as converting identifiers or small decimals into dates or dropping trailing zeros), all metrics are wrapped in explicit Excel string formula bindings:
`="[Value]"`

This guarantees structural integrity during downstream engineering tasks, manual audits, or when feeding this matrix directly into machine learning pipelines (e.g., XGBoost, Random Forests, or Neural Networks) for synthetic market classification tasks.
