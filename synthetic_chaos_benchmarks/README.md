# 🧬 Synthetic Chaos Benchmarks: Cascading Ring Generators

This directory contains high-performance synthetic dataset generators designed to evaluate, stress-test, and calibrate non-linear time-series profilers, chaotic spectral analyzers, and advanced mathematical sequence classifiers (such as the core engine of the **OEIS Mega Atlas**).

Unlike standard benchmark generators that rely on simple "Signal + Noise" architectures, these pipelines implement a **Multi-Layered Cascading Ring Deterministic Chaos** framework. 

---

## 🧠 Scientific Rationale & Core Concepts

In real-world complex systems (e.g., financial market micro-structures, quantum vortex dynamics, biological signal pathways), fundamental mathematical laws rarely appear in isolation. They are typically nested, feedback-looped, and obscured by environmental noise. 

To detect these hidden "genetic codes" within numerical sequences, analytical софт requires a highly rigorous testing environment. These generators solve this by creating sequences that:
1. Originate from a deterministic numerical backbone (\(x = [1, 2, ..., 100]\)).
2. Sequentially pass through **5 distinct non-linear mathematical rings (transformation stages)** chosen deterministically via a sliding phase window out of a 7-operation pool.
3. Are heavily masked by a **1% continuous stochastic mutation layer (White Gaussian/Uniform Noise)** at the single-element level.

Every generated sequence is automatically embedded with a permanent **Genetic Passport** (`Passport_Formula`). This ensures absolute ground-truth tracking, allowing unsupervised clustering algorithms to be precisely benchmarked on their ability to reconstruct the original 28 hidden mathematical lineages out of the distorted 980-row dataset matrix.

---

## 🛠 Generator Architectures

### 1. Multi-Field Cascading Ring Generator (`generator_multi_ring.py`)
This engine simulates an evolutionary environment where sequences migrate across completely different mathematical paradigms. It forces the analytical pipeline to differentiate between disparate structural behaviors (linear transformations, pure trigonometric loops, and modular arithmetic steps).

* **The 7-Ring Mathematical Pool:**
  * **Ring 0 (Scaling):** Linear compression/dilation (\(\frac{x}{20.0}\)).
  * **Ring 1 (Log-Modulation):** Exponentially-scaled logarithmic expansion (\(x \cdot \ln(\vert{}x\vert{} + \epsilon)\)).
  * **Ring 2 (Trigonometric Phase Shift):** High-amplitude sinusoidal wave wrapping (\(x + 15 \cdot \sin(x)\)).
  * **Ring 3 (Golden Ratio Scaling):** Spatial stabilization via the Fibonaccian constant (\(x \cdot 1.618\)).
  * **Ring 4 (Non-Linear Power Compression):** Monotonic power deformation with sign preservation (\(\text{sign}(x) \cdot \vert{}x\vert{}^{1.05}\)).
  * **Ring 5 (Discrete Modular Displacement):** Non-continuous grid quantization (\(x + 3 \cdot (x \pmod 7)\)).
  * **Ring 6 (Chaotic Wave Interference):** Asymmetric cosinusoidal friction loop (\(x - 8 \cdot \cos(x)\)).

### 2. Pure Logarithmic Cascade Generator (`generator_pure_logs.py`)
This represents an **advanced stress-test** for higher-order statistical metrics (such as the *Hurst Exponent*, *Permutation Entropy*, and *Takens' 3D Phase Space Geometry Axis Distribution*). All 7 operations in the pool are strictly restricted to logarithmic variants of different bases, scaling factors, and shift-windows. 

To the naked eye or linear regressions, all 980 rows look like identical logarithmic curves. The analyzer must look deep into the micro-topology of the sequence to isolate the hidden sub-lineages.

* **The 7-Ring Pure Logarithmic Pool:**
  * **Ring 0 (Natural Log):** Base-\(e\) scaling (\(15.0 \cdot \ln(\vert{}x\vert{} + \epsilon)\)).
  * **Ring 1 (Decimals):** Base-10 metric scaling (\(50.0 \cdot \log_{10}(\vert{}x\vert{} + \epsilon)\)).
  * **Ring 2 (Binary Log):** Base-2 information tracking (\(8.0 \cdot \log_{2}(\vert{}x\vert{} + \epsilon)\)).
  * **Ring 3 (Sinusoidal Log Wave):** Dynamic transcendental log-modulation (\(x \cdot \ln(\vert{}\sin(x) \cdot 10\vert{} + \epsilon)\)).
  * **Ring 4 (Argument Power Log):** Polynomial transformation reduction (\(\frac{\ln(x^2 + \epsilon)}{2.0}\)).
  * **Ring 5 (Phi-Shifted Log):** Constant translation via the Golden Ratio (\(1.618 \cdot \ln(\vert{}x + 25.0\vert{} + \epsilon)\)).
  * **Ring 6 (Feedback Log Loop):** Self-referential iterative reduction (\(x - 12.0 \cdot \ln(\vert{}x\vert{} + \epsilon)\)).

### 3. Chromatic Noise Cascade Generator (`generator_chromatic_noise_rings.py`)
This generator is the ultimate test of an analytical system's capability to untangle real-world multi-spectral physical data. Instead of treating colored noise as an external destructive factor, this engine uses **colored noises as structural building blocks** interwoven with non-linear deterministic functions.

It creates sequence structures mirroring natural and artificial phenomena (e.g., neural EEG signals, deep-ocean turbulence, or highly volatile cryptocurrency order books) where multiple noise spectra coexist simultaneously.

* **The 7 Chromatic & Mathematical Rings:**
  * **Ring 0 (Red Noise / Brownian):** Integrates strong physical memory and macro-trends via a cumulative brownian walk (\(1/f^2\) energy distribution).
  * **Ring 1 (Log-Scaling):** Forces a deterministic non-linear compression block (\(\ln(\vert{}x\vert{})\)).
  * **Ring 2 (Blue Noise):** Inject high-frequency violences via differentiated white noise, mimicking high-pitch hardware static (\(f\) energy distribution).
  * **Ring 3 (Pink Noise / Flicker):** Applies the universal \(1/f\) natural fractal harmony resonance, introducing long-term balanced cross-correlations.
  * **Ring 4 (Black Noise / Intermittent):** Simulates catastrophic system failures. It injects severe, isolated macroscopic anomalies (spikes between \(15\sigma\) and \(30\sigma\)) separated by long periods of low-variance dormancy.
  * **Ring 5 (Golden Ratio Warp):** Applies non-linear power warping stabilized by the Phi constant (\(1.618 \cdot \vert{}x\vert{}^{1.05}\)).
  * **Ring 6 (Modular White Chaos):** Combines discrete lattice shifts with pure uncorrelated zero-memory Shannon entropy (\(White\ Noise\)).

* **Target Evaluation Metrics:** This dataset tests if your profiler can read through conflicting noise signatures. The *Hurst Exponent* must separate the heavy memory of Red Rings from Pink Rings, while the *FFT Spectral Entropy* and *Permutation Entropy* must accurately pinpoint at which stage the high-frequency Blue or catastrophic Black rings were injected.

### 4. Quadrilateral Area Cascade Generator (`generator_quadrilateral_area_rings.py`)
This generator establishes a direct topological bridge between spatial geometry, aperiodic tilings (like *Hat* and *Spectre* clusters), and 1D algebraic sequences. Instead of equations, the core backbone of these sequences is grown from the **exact vector areas of 4 alternating multi-scale quadrilaterals** generated dynamically in 2D space.

* **The 4 Geometric Structural Foundations:**
  * **Parallelogram:** Area generated via dynamic base-height vector scaling.
  * **Trapezoid:** Area calculated via asymmetric multi-base lattice parameters.
  * **Rhombus:** Grown via orthogonal diagonal intersections.
  * **Rectangle:** Built from classic length-width boundary limits.

* **The 7 Geometric Transformation Rings:**
  * **Ring 0 (Spatial Compression):** Linear area deflation (\(\frac{x}{25.0}\)).
  * **Ring 1 (Log-Warping):** Logarithmic distortion of the continuous geometric fabric (\(\ln(\vert{}x\vert{})\)).
  * **Ring 2 (Sinusoidal Grating):** Wave-like torsion mimicking crystalline lattice shifts (\(x + 20 \cdot \sin(x)\)).
  * **Ring 3 (Golden Ratio Modular Scale):** Proportional dilation using the aperiodic tiling constant (\(x \cdot 1.618\)).
  * **Ring 4 (Power Deformation):** Monotonic vector extension (\(\vert{}x\vert{}^{1.03}\)).
  * **Ring 5 (Lattice Quantization):** Discrete mosaic step shift representing periodic grid boundaries (\(x + 4 \cdot (x \pmod 9)\)).
  * **Ring 6 (Cos-Interference):** Quasi-periodic aperiodic friction noise to obscure regular patterns.

* **Target Evaluation Metrics:** This benchmark tests the engine's capability to extract multidimensional spatial symmetries from 1D data. The *Takens' 3D Snake Geometry* analyzer should reconstruct the structural boundaries of the original geometric shapes, proving that the profiler can reverse-engineer spatial dimensions directly from raw number distributions.

---

## 🔧 Data Customization & Parameter Tuning

Both scripts are written using clean, vectorized Python code (`numpy` and `pandas`) and can be easily customized to fit specific experimental requirements:

### Changing Sequence Length
By default, each row contains 100 dimensions (`Num_1` to `Num_100`). To change the sequence resolution (e.g., to evaluate how algorithms perform on short vs long time-series), locate the initialization line inside the core function:
```python
# To scale sequence length to 500 points:
x = np.arange(1, 501, dtype=float)
```
*Note: If you change this, ensure your final dictionary-packing loop dynamically maps to the new dimension size.*

### Adjusting Mutation (Noise) Intensity
The stochastic mutation layer is currently set to an industrial 1% standard deviation baseline (`[0.99, 1.01]`). To test the absolute limits and breakdown thresholds of your analytical model, modify the noise bounds:
```python
# For a high-noise environment (5% structural mutation):
pure_random_noise = np.random.uniform(0.95, 1.05, size=100)

# For a pristine/zero-noise deconstruction test:
pure_random_noise = np.ones(100)
```

### Expanding the Dataset Volume
The matrix volume is defined by the number of core algorithmic lineages (`total_variants = 28`) and individual mutations per lineage (`mutations_per_variant = 35`), creating a 980-row dataset. To scale this into the Big Data domain (e.g., for training deep learning models via *Grokking* simulation), adjust the loops:
```python
# Scale to 10,000+ synthetic sequences:
total_variants = 100
mutations_per_variant = 100
```

---

## 🎯 How to Use with OEIS Mega Atlas

1. Execute the scripts in your root or subdirectory environment:
   ```bash
   python generator_multi_ring.py
   python generator_pure_logs.py
   ```
2. The pipelines will output clean, production-ready files: `synthetic_rings_980_dataset.csv` and `synthetic_pure_logs_980.csv`.
3. Feed these files directly into the `oeis_processor.py` pipeline. 
4. **Validation Step:** Exclude the first 4 columns (`Global_Row_ID`, `Class_ID`, `Mutation_ID`, `Passport_Formula`) during the mathematical feature calculation stage. Once the metrics are computed, perform unsupervised PCA, t-SNE, or K-Means clustering. If the resulting clusters match the `Class_ID` passport tags, the analytical engine has successfully isolated the hidden эмерджентная математика from the chaotic noise.
