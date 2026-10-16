# Statistical preparation

These are prespecified model definitions and synthetic planning tools, not study
results. The main analysis CLI still exports descriptive tables. No live-data
confirmatory report has been produced.

## Environment

Validated: R 4.5.3, lme4 2.0-6, MASS 7.3-66, renv 1.3.1. `renv.lock` pins the R
packages and their dependencies. Restore with R 4.5.3 and renv from the
`experiment/` directory:

```r
renv::restore(project="statistics")
```

For the exact tested macOS-arm64 binaries and runtime dependencies, micromamba
can create a separate environment from `conda-osx-arm64.lock`. This platform
lock is not portable to Linux or Windows; use the R package lock there and
revalidate. Keep installed environments, libraries and outputs outside Git.

## Models and inputs

`models.R` defines `load_primary(h, analysis_directory)`, `fit_primary(h, data)`
and `primary_contrast(h, fit)`. The loader maps public CSV columns to the exact
factors and reference levels in the preregistration, selecting group conditions
and actual notice recipients where required. It does not reinterpret missing
outcomes. The main CLI has already applied run/agent exclusions.

H1–H3 fit reward × wording × persona logistic models with a run intercept; H4
fits clarity × conflict. H5 models eligible-agent volunteering in run-ending
sacrifice with benefit × poisoning condition, individual poisoning, and run and
run/agent intercepts. H6 models run posting counts with group cue × reward scheme
× population size, a log included-population offset, and negative-binomial
dispersion. A random run intercept is not identifiable with one row per run.

The six primary contrasts are defined in one place. Risk differences are at
random effects zero, averaged over balanced experimental-factor grids, rather
than a fully population-marginal estimand. H5 standardization respects the
assigned poisoned fractions. H6 returns a log rate ratio (exponentiate for the
rate ratio). Wald uncertainty conditions on estimated variance parameters;
report that approximation and singular flags. No function silently replaces a
failed model with an easier one. Apply `p.adjust(primary_p, method="holm")` once
to the six prespecified primary p-values; retain non-estimable tests as NA, and
use `n=6` if a reporting subset omits them.

## Planning workflow

From `experiment/`:

```sh
python planning.py --out /tmp/swarm-planning-fresh
Rscript statistics/test_models.R
Rscript statistics/power.R H1 5 1000 0.5 0.10 0.10 /tmp/h1-scenario.csv
Rscript statistics/power.R H5 5 1000 0.01 0.10 0.01 /tmp/h5-scenario.csv
```

Power arguments are hypothesis, seeds per primary condition, replicates,
assumed baseline, assumed ICC, effect, output, and optional NB dispersion.
H6 baseline means posts per agent and effect is a rate ratio; ICC is unused.
H5 baseline means eligible-agent row probability, and effect is an absolute
probability difference. H5 simulation preserves the single-winner request and
shrinking active population, and rejects unattainable input targets. It is a
simplified nuisance scenario generator, not the actual agent simulator.

Binary ICC is latent-logit run clustering. H5 currently generates no additional
agent-specific heterogeneity; the fitted agent intercept is retained and may be
singular. If pilot evidence requires broader nuisance scenarios, revise the
generator explicitly before freezing. Failed fits are non-rejections in power
summaries, and counts of failures/singularities remain visible. Two-replicate
smoke checks validate mechanics only; they do not calibrate inference or supply
usable power estimates.

The Python screening grid uses design-effect/normal approximations, not fitted
models, to shortlist candidates. Its costs distinguish context-limit upper
bounds (including maximum retries) from assumed 10k-input-token cache scenarios
(with one successful attempt). Neither uses mock statistics
as measured pilot evidence. H5's original 10-point target was infeasible; the
project lead approved a one-percentage-point target while retaining the eligible-agent
outcome. This removes that ceiling conflict, not the need for power validation.

After step 4, declare central and conservative nuisance scenarios based on pilot
measurements, retaining conservative Sonnet ranges when only Haiku was sampled.
Run at least 1,000 replicates for each shortlisted candidate and scenario. Combine
`.summary.csv` files into a CSV with `hypothesis,scenario,seeds,replicates,power,
mc_se,failures`, then:

```sh
python statistics/select_allocation.py --results /path/to/scenarios.csv \
  --scenarios central conservative --costs /path/to/measured-cost-forecasts.json \
  --budget APPROVED_STUDY_BUDGET --out /path/to/allocation.json
```

The cost JSON maps seed counts to full-study forecast dollars based on measured
pilot calls, including retries and secondary conditions. It is not the study's
spending authorization. The selector requires every declared scenario for all
six tests, 1,000+ replicates, at most 5% failed fits, and Wilson lower 95% Monte
Carlo power ≥80%, using sizing alpha .05/6. Choose the smallest common primary
seed allocation within budget; secondary condition seed lists stay fixed unless
explicitly revised. Infeasibility is an output, not a reason to delete a test.

Final freeze review must also assess null calibration and model adequacy under
winner-limited H5 data, parameter uncertainty, pilot gates and missingness. An
assumption-based planning script cannot certify those from a mock run.
