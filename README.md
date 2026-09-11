# 🛸 OEIS Mega Atlas: Nonlinear & Statistical Sequence Analyzer

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

## 🎭 AI-Driven Automated Classification

Based on the combined 37 features, the pipeline automatically assigns a complex behavioral verdict to each sequence:
* **Absolute Crystalline Trend:** (цифры тупо растут вверх, как твои долги по учебе/работе) Perfect linear/exponential growth with ultra-low permutation entropy.
* **Cosmic Swirling Attractor:** (просто набор цифр, которые по спирали уныло сходятся к нулю) Deep 3D orbital trajectory with fading Z-axis variance and extreme rotational force.
* **Hyper-Coral of the Higher Order:** (полная нечитаемая фигня и каша, в которой даже ИИ ничего не понял) High-entropy multi-dimensional complex structures.
* **Tectonic Shift / System Failure:** (все сломалось, данные улетели в стратосферу, мы все ...) Extreme step anomalies or massive skewness.
* **High-Entropy White Noise:** (шум телевизора без антенны, полезности ноль) High spectral entropy coupled with a low Hurst exponent.
* **Natural Benford Law:** Sequences conforming perfectly to logarithmic first-digit distribution.

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
