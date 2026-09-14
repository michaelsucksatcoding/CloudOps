# Reproducible Local Evaluation

Run `python -m experiments.run_local_evaluation` from the repository root.
The script writes measured raw output to `experiments/results/`; run
`python -m experiments.analyze_results` to derive summaries and SVG figures.

The experiment uses deterministic simulator labels: `normal` is negative and
the remaining simulator scenarios are positive. These labels are synthetic and
must not be presented as production-ground-truth labels.
