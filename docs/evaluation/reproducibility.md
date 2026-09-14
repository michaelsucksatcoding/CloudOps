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
