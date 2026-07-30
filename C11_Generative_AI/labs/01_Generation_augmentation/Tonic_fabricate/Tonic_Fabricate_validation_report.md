# Synthetic Data Generation — Model & Validation Report

**Dataset:** Medical Insurance Charges
**Source rows:** 1,338 · **Synthetic rows:** 1,338 (1×)
**Columns preserved:** `age, gender, bmi, children, smoker, region, expenses`

---

## 1. Modeling Approach

The generator uses a **hybrid conditional model**: feature columns are synthesized non-parametrically, and the target column (`expenses`) is synthesized from a supervised regression model with a stochastic residual component. This two-stage design reproduces both the marginal shape of every column *and* the dependency structure between the cost driver variables and the charge.

| Stage | Technique | Purpose |
|---|---|---|
| **A. Feature synthesis** | Empirical resampling (bootstrap) + jitter | Reproduce each predictor's real distribution while creating novel rows |
| **B. Target synthesis** | Ordinary Least Squares (OLS) regression + bootstrapped residuals | Learn how `expenses` depends on the features, then add realistic noise |
| **C. Guardrails** | Range clamping + precision rounding | Enforce domain validity (no negatives, correct decimals) |

**Why this method rather than a black-box (GAN/VAE):** with only 1,338 rows and a well-understood cost structure, an interpretable regression + bootstrap approach is more stable, cannot memorize/leak source rows, and gives auditable coefficients. It is a form of **conditional density estimation** — the same principle behind sequential synthesizers.

---

## 2. Data Distribution Handling

Each column was synthesized using a method matched to its type:

| Column | Type | Handling |
|---|---|---|
| `age` | integer 18–64 | Bootstrap from empirical values + uniform jitter (±2), clamped |
| `bmi` | continuous | Bootstrap + Gaussian jitter (σ≈1.6), clamped to [16, 53.1], 1-decimal |
| `children` | ordinal 0–5 | Direct empirical resample (exact category frequencies preserved) |
| `gender` | binary | Categorical draw from empirical probabilities (50.5% / 49.5%) |
| `smoker` | binary | Categorical draw (20.5% yes) |
| `region` | 4-level | Categorical draw from empirical shares |
| `expenses` | continuous, right-skewed | **Model-predicted + residual bootstrapped within smoker group** → preserves skew & heteroscedasticity |

The **jitter** on continuous predictors is what introduces "meaningful variation" — synthetic rows are near, but not equal to, real feature combinations. Residuals are resampled **within smoker strata** so that the much larger variance among smokers is faithfully reproduced rather than averaged away.

---

## 3. Feature Relationships Learned

The OLS model recovered the true cost structure of the dataset. Coefficients (effect on annual `expenses`, in $):

| Feature | Coefficient | Interpretation |
|---|---|---|
| Intercept | −3,587 | baseline |
| **age** (per year) | **+263** | older → higher cost (near-linear) |
| **bmi** (per unit) | **+62** | mild positive effect for non-smokers |
| children (per child) | +520 | small positive |
| **smoker = yes** | **+13,578** | large main effect |
| **smoker × obese (bmi≥30)** | **+19,462** | **dominant interaction** — smoking + obesity |
| gender = male | −494 | negligible |
| region (NW / SE / SW vs NE) | −279 / −783 / −1,216 | minor geographic variation |

The critical insight captured is the **smoker × BMI interaction**: a smoker with BMI ≥ 30 costs ~$33k more than the baseline, which is why the four cost segments are so distinct. This relationship is fully preserved in the synthetic output (validated below).

---

## 4. Performance Metrics

### 4.1 Model fit (on source data)

| Metric | Value | Meaning |
|---|---|---|
| **R²** | **0.863** | Model explains 86.3% of variance in `expenses` |
| **RMSE** | $4,473 | Typical prediction error (vs. mean charge $13,270) |
| **MAE** | $2,465 | Median-scale absolute error |

An R² of 0.86 is essentially the ceiling for this dataset — the residual variance is inherent randomness in individual medical costs.

### 4.2 Detection / Distinguishability — the "AUC" metric

A **logistic-regression discriminator** was trained to classify rows as real vs. synthetic (70/30 train-test split, all 7 features + expenses, standardized). If synthetic data is indistinguishable from real, this classifier should do no better than a coin flip (AUC = 0.50, accuracy = 0.50).

| Metric | Value | Ideal | Verdict |
|---|---|---|---|
| **Detection AUC** | **0.486** | 0.50 | ✅ Indistinguishable |
| **Detection accuracy** | **0.498** | 0.50 | ✅ No better than random |
| Test set size | 803 rows | — | — |

**Interpretation:** AUC of 0.486 (below/at 0.5) means a trained adversary **cannot separate** synthetic rows from real ones — the strongest single indicator of high-fidelity synthesis. Equivalent utility score (`1 − |AUC − 0.5| × 2`) ≈ **0.97**, well above your 0.80 target.

### 4.3 Per-column distribution similarity

**Kolmogorov–Smirnov statistic** (continuous/ordinal — lower = closer, 0 = identical):

| Column | KS | Similarity |
|---|---|---|
| age | 0.018 | 98.2% |
| bmi | 0.022 | 97.8% |
| children | 0.025 | 97.5% |
| expenses | 0.044 | 95.6% |

**Total Variation Distance** (categorical — lower = closer):

| Column | TVD | Similarity |
|---|---|---|
| gender | 0.001 | 99.9% |
| smoker | 0.016 | 98.4% |
| region | 0.029 | 97.1% |

All columns are within 0.05 distance — statistically very close matches.

### 4.4 Correlation preservation

Pearson correlation with `expenses`, source vs. synthetic:

| Relationship | Source r | Synthetic r | Δ |
|---|---|---|---|
| age ↔ expenses | 0.299 | 0.285 | 0.014 |
| bmi ↔ expenses | 0.199 | 0.137 | 0.062 |
| **smoker ↔ expenses** | **0.787** | **0.780** | 0.007 |
| age ↔ bmi | 0.109 | −0.012 | 0.121 |

The **dominant driver (smoker → expenses)** is reproduced almost exactly. The one weak spot is the incidental `age↔bmi` correlation (0.11 in source, ~0 in synthetic) — expected, since features are resampled independently. It is a minor, non-predictive association and does not affect cost realism.

### 4.5 Segment-level fidelity (business-rule check)

| Segment | Source avg | Synthetic avg | Error |
|---|---|---|---|
| non-smoker / normal BMI | $7,977 | $8,104 | 1.6% |
| non-smoker / obese | $8,843 | $9,084 | 2.7% |
| smoker / normal BMI | $21,363 | $21,622 | 1.2% |
| smoker / obese | $41,558 | $41,622 | 0.2% |

### 4.6 Privacy / leakage

| Check | Result |
|---|---|
| Exact duplicate rows vs. source | **0 / 1,338** |

No source record was copied — the dataset is genuinely synthetic.

---

## 5. Overall Assessment

| Dimension | Score | Target | Status |
|---|---|---|---|
| Model explanatory power (R²) | 0.863 | — | ✅ |
| Indistinguishability (detection utility) | ~0.97 | ≥0.80 | ✅ Exceeds |
| Marginal distribution match (avg) | ~97% | ≥0.80 | ✅ Exceeds |
| Key correlation preservation | 0.007 Δ on top driver | — | ✅ |
| Segment cost accuracy | ≤2.7% error | — | ✅ |
| Privacy (no leakage) | 0 duplicates | — | ✅ |

**Conclusion:** The synthetic dataset comfortably surpasses the ~80% similarity goal on every axis measured — a detection classifier performs at chance level (AUC 0.486), all column distributions match to within 95–99%, and the core cost relationships are reproduced within a few percent, all while introducing genuine row-level variation and leaking zero original records.

---

## Notes on Terminology

"Accuracy" and "AUC" in synthetic-data validation refer to the **detection/distinguishability** classifier (§4.2), *not* a predictive label task (this dataset has no classification target). An optional **Train-on-Synthetic-Test-on-Real (TSTR)** experiment — training a cost model on the synthetic data and measuring its R² on the real data — can be added as a further utility metric.

*Report generated by Tonic Fabricate.*
