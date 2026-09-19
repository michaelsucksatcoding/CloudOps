# Reproducibility

Use the project virtual environment and run:

```powershell
.venv\Scripts\python.exe -m experiments.run_local_evaluation
.venv\Scripts\python.exe -m experiments.analyze_results
```

Inputs and seeds are versioned in
`experiments/configs/local-evaluation.json`. The first command overwrites the
raw JSON measurement; the second derives a CSV and SVG chart from it. Record
the execution date, Python version, and dependency versions from the JSON when
comparing runs.

## Verified run-to-run reproducibility

Two runs have been compared under the same seeded experimental configuration:
the committed 2026-09-14 baseline and the fresh 2026-09-18 run (same Python
3.13.5 / scikit-learn 1.9.0 environment, same simulator seed and hyperparameters).

The **classification results were exactly reproducible** across the two runs:

- Identical: TP, FP, TN, FN counts.
- Identical: precision, recall, F1, false-positive rate, false-negative rate.
- Identical: all per-scenario detection rates.

Only the following varied between runs:

- `executed_at` timestamp.
- Inference timing measurements.
- Pipeline timing measurements.
- API timing measurements.

Timing measurements varied between runs, as expected for performance
measurements. Runtime measurements are **not** deterministic, and
performance numbers from one run must not be described as reproducible or
guaranteed.