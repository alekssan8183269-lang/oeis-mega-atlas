# 🛸 OEIS Mega Atlas: Nonlinear & Statistical Sequence Analyzer

высокоточный Цифровой Профайлер (или Спектрометр математических структур), расширили базу теперь не 37 данных вытаскиваем а более 100+ в таблицу. пострадала скорость с 14000тысяч рядов до 800 в минуту.

---

A high-performance mathematical pipeline designed for the comprehensive extraction of **37 topological, statistical, and chaotic metrics** from numerical series. It transforms one-dimensional sequences into multidimensional trajectories and applies advanced mathematical filters to classify data into unique behavioral archetypes.

Optimized to run safely on budget hardware (e.g., Core i5, 8GB RAM) using strict memory-safe batch processing.

---

## 🧠 Key Features & Mathematical Engine

The core engine dissects sequences across **6 advanced mathematical dimensions** (yielding a 40-column comprehensive dataset):

1. **Higher-Order Statistics & Percentiles:** Skewness, Kurtosis, Coefficient of Variation, and Step Anomaly Ratios to catch sudden shifts.
2. **Quantum & Dynamical Entropy:** Shannon Entropy, Permutation Entropy (micro-pattern direction analysis), and a fast matrix approximation of Approximate Entropy (ApEn).
3. **Autocorrelation Echo-Lags:** Deep Pearson correlation analysis up to 5 lags to detect hidden periodicities.
4. **Deep Fourier Spectrum Analysis:** FFT Energy, Main/Median Frequencies, Peak Amplitude, and Spectral Entropy to measure frequency purity.
5. **3D Snake Geometry & Tensor Analysis (Takens' Theorem):** Reconstruction of 1D series into a 3D phase space. Computes Cloud Radius, Total Snake Length, SVD/PCA Axis Distribution, and Angular Rotational Force (`vector_rot_force`).
6. **Fractals & Benford's Law Deviations:** Grassberger-Prokaccia Correlation Dimension, Hurst Exponent (long-term memory), and a full Benford's Law Chi-Square style deviation test on first digits.

---

## 🎭 Automated Sequence Classification

The pipeline uses 37 topological and statistical features to classify integer sequences:

*   **Absolute Crystalline Trend** *(Linear / Exponential Growth)* — A predictable monotonic progression with ultra-low permutation entropy.
*   **Cosmic Swirling Attractor** *(Damped 3D Spiral)* — A 3D orbital trajectory with decaying Z-axis variance and rotational vector force.
*   **Hyper-Coral of the Higher Order** *(Structured Chaos)* — High-entropy, multi-dimensional structures possessing hidden internal topology.
*   **Tectonic Shift / System Failure** *(Critical Anomaly)* — Severe step anomalies indicating a radical shift in sequence behavior.
*   **High-Entropy White Noise** *(Pure Random Noise)* — High spectral entropy and low Hurst exponent with zero actionable information.
*   **Natural Benford Law** *(Logarithmic Distribution)* — Series fitting the logarithmic first-digit distribution, confirming unmanipulated data.

---

## 🚀 Performance & Architecture

* **Memory-Safe Batching:** Processes sequences in strict blocks of 20, wiping RAM continuously.
* **Hardware Friendly:** Integrated cooling delays (`time.sleep`) to prevent CPU thermal throttling.
* **Input Requirements:** Expects standard `stripped.gz` and `names.gz` database dumps from the **OEIS** (On-line Encyclopedia of Integer Sequences).

## 🛠️ Quick Start

1. Download `stripped.gz` and `names.gz` from official OEIS mirrors and place them in the project root directory.
2. Run the analyzer:
```bash
python main.py
```
3. Find your 40-column mathematical dataset in `oeis_mega_atlas_40fields.csv`.

---
*Developed with a passion for chaos, non-linear dynamics, and beautiful mathematics.*
