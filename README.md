# Compositional Rounding Certificates

This standalone artifact accompanies *Compositional Rounding Certificates for
Chunked Affine Scans*. It implements a bounded integer fixed-point recurrence,
a declared chunk-prefix lowering, ordered input-cover certificates, and an
exact checker.

## Environment and reproduction

Use Python 3.11 or newer and the standard library; there are no third-party
Python dependencies. Run from this directory on Windows or POSIX:

```sh
python -B scripts/reproduce.py
```

On POSIX, `./reproduce.sh` selects the same entry point using `python3`.

The default command regenerates cases in a temporary directory and compares
their bytes, rebuilds derived tables from retained raw records, checks stored
certificate lengths, audits the reference inventory, and runs finite checks
and boundary regressions. It writes derived CSV/JSON/TeX reports and
`results/reproduction.json` in this copy, but does not rerun timed experiments
or overwrite raw measurements/certificates. Use a disposable copy when you need
to preserve every shipped report byte.

For a new one-worker campaign followed by retained-evidence checking:

```sh
python -B scripts/reproduce.py --rerun-campaign --campaign-out ../campaign-output
```

The campaign output must not already exist and must be outside the shipped
`results/` tree. Fresh raw records, certificates, summaries, and worker output
go there; recorded manuscript measurements remain separate.

Check one retained certificate against its independent instance file:

```sh
python -B scripts/check_certificate.py results/certificates/frozen/case-001-fresh.json --instance cases/frozen/case-001.json
```

## Inputs and outputs

An instance declares signed word width, power-of-two scale, floor or
round-to-nearest-even rounding, saturation, initial state, affine matrices,
Cartesian input boxes, chunk length, association, and output tolerances.
The reference executes every update; the lowering quantizes transfer
summaries and evaluates causal prefixes from the incoming chunk carry.

- `cases/`: deterministic development, frozen, and long-horizon stress inputs.
- `src/fixedscan/`: arithmetic, analyses, producer, exact checker/baseline,
  leaf admission, transport, block projection, and reduction constructions.
- `results/raw/`: authoritative retained records by instance and method.
- `results/certificates/`: conclusive ordered-cover certificates.
- `results/*-metrics.csv`, `results/*-summary.json`, and
  `results/stress-by-horizon.csv`: derived campaign tables.
- `results/paper-results.tex`: manuscript rows generated from the same raw
  records and certificate files. `scripts/analyze_results.py` rebuilds these
  products and checks certificate byte counts; in a full project it also checks
  the existing `paper/generated-results.tex` without rewriting it.
- `results/current-replay/`: separate native-run data/logs, not replacement
  timings for the manuscript tables.
- `proofs/`, `claim_evidence_ledger.csv`, `reference-audit.csv`, and
  `external_resources.csv`: hand proofs, claim/evidence mappings, and provenance.

## Tests and additional coverage

```sh
python -B tests/run_all.py
python -B tests/test_exact_boundaries.py -v
python -B tests/test_scalar_summary_cache.py -v
python -B -m unittest discover -s tests -p test_trace_input_domain.py -v
python -B tests/test_association_coverage.py -v
```

`tests/run_all.py` checks arithmetic paths, exact oracles, stored certificates
and mutations, reductions, transport, and recorded-result reconciliation; it
writes `results/test-summary.json`. The separate tests cover deadlines,
admission, serialization and output isolation, scalar summary reuse, legal
input domains, and non-inert association controls. Their method/assertion counts
are different units from campaign cases and must not be pooled as samples.

The separate 144-instance association cohort has its own declared inputs and
independent literal evaluator. To generate it, choose another absent directory:

```sh
python -B scripts/association_coverage.py --out ../association-study
```

This output must be outside inherited `cases/` and `results/`.
[docs/association-coverage.md](docs/association-coverage.md) specifies the
unfiltered product, fixed tolerances, and comparison rules.
[docs/experiment-design.md](docs/experiment-design.md) describes frozen/stress
denominators and measurement interpretation.
[docs/validation-contract.md](docs/validation-contract.md) maps acceptance
boundaries to tests.

## Result interpretation and conditions

The frozen suite has 72 cases and five methods: 33 safe and 39 violating
instances for each method, with 288 accepted cover certificates. Its chunks
have length two, so the equally frequent association labels do not establish
nontrivial tree-shape coverage. The inherited `stable` family label is not a
strict contraction condition. Stress `unknown` outcomes remain in the
denominator; they are not safe conclusions.

A conclusive certificate covers every proven-safe output and supplies a
singleton witness for the first failing output. The checker independently
recomputes exact leaf ranges and enforces canonical splitting and left-first
traversal, establishing the earliest failing output and lexicographically first
violating prefix. A producer `unknown` result is not accepted as a proof.

Scalar leaves use exact finite-state DP. Multidimensional leaves admit complete
enumeration only up to 100,000 points; larger leaves require subdivision or
`unknown`. Producer/checker leaf admission shares structural eligibility, not
arithmetic bounds. The checker has a closed JSON schema and enforces integer
types, duplicate-key rejection, and byte/node/depth/model-size limits. Complete
traces must stay inside each declared input box.

Frozen tasks have 20-second internal and 5,000-node cover limits. Stress cover
tasks have five seconds and 20,000 nodes; exact DP has 12 seconds. These
deadlines are cooperative, with worker termination after the internal limit
plus five seconds. Completed deterministic searches have reproducible
claim-bearing statuses, accepted checks, and node counts; timed partial
progress and CPU/wall/RSS are host dependent. Unix RSS is unavailable on Windows.

The fresh native validation in `results/native-validation.zip` preserves all
88 complete input files before their workers execute, including `stress-005`,
`stress-009`, and `stress-013`. All 440 tasks completed without worker errors;
334 certificates passed an additional checker replay and 18 cover tasks returned
`unknown`. Every status and every conclusive certificate body and node count
agrees with the retained campaign. The archive includes the actual executable
sources, environment, worker output and verification report.

The earlier native archive still retains complete certificate-embedded inputs
for 85/88 instances. Its three missing inputs are not retroactively recovered
by this new execution. Fresh host timings stay separate from the manuscript's
historical measurements. The runner now captures complete inputs for every
outcome and rejects resumed records lacking their input binding.

Scalar summary reuse is layer-local, keyed by complete chunk-input tuples and
capped at 4,096 entries. All reference/carry transitions still run, and summaries
respect the declared association; uncached tuples compute normally at the cap.
This is not a measured memory or speedup claim. Hand proofs are not mechanized
by these finite tests, and the generated suites do not measure trained-model,
accelerator, or deployment performance.

## License

Original code, generated cases, results, and documentation are MIT-licensed in
`LICENSE`. No ACM class or bibliography-style file is included in this standalone
artifact.


## Paper figures

Canonical repository: https://github.com/Haoyi-Zhang/RoundScan.

The optional relationship diagrams are generated by `plot_schematics.py`.
Install `requirements-figures.txt`, then run:

```sh
python -B plot_schematics.py --outdir ../paper/figures
python -B check_schematics.py
```

These commands do not run the scientific campaign. The separate statistical
figure script ships with the paper and reads its retained table macros.
