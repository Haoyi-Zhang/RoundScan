# Compositional Rounding Certificates

This repository is the standalone artifact for *Compositional Rounding Certificates for Chunked Affine Scans*. It specifies a bounded integer fixed-point recurrence, a declared chunk-prefix lowering, proof-producing ordered input covers, and an exact checker. The implementation has no third-party Python dependency.

## What is checked

An instance embeds signed word width, power-of-two scale, floor or round-to-nearest-even rounding, saturation, initial state, time-varying affine matrices, Cartesian input boxes, chunk length, association rule, and one tolerance vector per output. The reference executes every recurrence update. The lowering quantizes affine transfer summaries and evaluates every causal prefix from the same incoming chunk carry.

A conclusive ordered-cover certificate contains one root per proven-safe output and, when the contract fails, a singleton witness at the first failing output. The checker recomputes exact leaf ranges. It also enforces canonical first-nonsingleton splitting and left-before-right traversal, so an accepted violation certificate establishes the lexicographically first violating prefix at the earliest failing output. An `unknown` producer result is never accepted as a proof.

## Repository map

- `src/fixedscan/`: concrete semantics, analyses, producer, checker, exact baseline, block projection, and executable reduction constructions.
- `cases/`: deterministic development, frozen, and long-horizon stress instances.
- `results/raw/`: one raw record per instance and method.
- `results/certificates/`: all conclusive ordered-cover certificates.
- `results/*-metrics.csv` and `results/*-summary.json`: collected campaign results.
- `tests/run_all.py`: arithmetic cross-checks, exact-oracle comparisons, certificate and mutation checks, reduction checks, and result reconciliation.
- `proofs/`: hand proofs and claim-level statement index. These are not a mechanized formalization.
- `claim_evidence_ledger.csv`: paper claim to theorem, implementation, and result mapping.
- `reference-audit.csv`: one provenance row for every manuscript reference.
- `external_resources.csv`: scholarly/software resources and acquisition notes.

## Reproduce the checked evidence

Python 3.11 or newer is sufficient.

```sh
./reproduce.sh
```

The default path regenerates all deterministic case files in a temporary directory, compares them byte-for-byte, rebuilds summaries from the raw records, audits the 30-entry scholarly-reference inventory, independently checks every stored certificate, reruns all finite oracles and mutation tests, and writes `results/reproduction.json`. It deliberately does not overwrite recorded wall/CPU timings.

To rerun the complete one-worker campaign before the same checks:

```sh
./reproduce.sh --rerun-campaign
```

Each frozen task has a 20-second internal limit and 5,000-node cover limit. Each stress cover task has a 5-second internal limit and 20,000-node limit; the exact dynamic-program baseline gets 12 seconds. `unknown` is an intended resource-bound outcome. Timings are machine dependent, while statuses, certificate acceptance, node counts on completed deterministic searches, and test assertions are the claim-bearing quantities.

Check one certificate directly:

```sh
python3 scripts/check_certificate.py \
  results/certificates/frozen/case-001-fresh.json \
  --instance cases/frozen/case-001.json
```

## Recorded evidence

The frozen suite contains 72 instances and 33,804 exact prefix evaluations. All five methods classify the same 33 safe and 39 violating instances. The four cover producers yield 288 certificates, all accepted by the checker. Independent interval covers use 24,774 nodes; each paired policy uses 3,260. The three paired residual-sharing policies therefore have identical final cover topology on this suite.

The 16 stress instances have horizons 8, 16, 32, and 64. Exact finite-state dynamic programming resolves 16/16; paired covers resolve 12/16; independent interval covers resolve 10/16. Unresolved cases remain `unknown` rather than being counted as safe.

The test suite records 106,611 assertion units. It includes 45,072 producer/checker concrete-prefix cross-checks, 45,072 exact-oracle prefix evaluations, 334 accepted stored certificates, 53 rejected mutation/parser/admission inputs, 48 dynamic-program/exhaustive association checks, 4,914 block-factorization prefix checks, 832 fixed-width circuit assignment/mode executions, 867 packed-CNF formulas over 6,474 assignments, and 30 verified scholarly-reference records.

## Trusted boundary and limitations

The checker accepts a closed JSON schema: semantic integers must be JSON integers (not booleans, floats, or strings), duplicate keys and nonstandard numeric constants are rejected, and explicit byte/node/depth plus model-size limits are enforced. It uses a separately written concrete-arithmetic module and does not import the producer's abstract interpretation. It remains code produced and reviewed within one research process, not an independently authored or machine-verified checker. General theorem arguments in `proofs/arguments.tex` are hand proofs. Finite tests validate implemented cases but do not mechanize those general arguments.

The generated suites are discriminating semantic and certificate tests, not trained-model, accelerator, deployment, or workload-performance evidence. Input boxes are Cartesian. The implementation uses one uniform scale and rounding mode per instance. The exact checker enumerates small multidimensional leaves and uses a scalar finite-state dynamic program for large scalar prefixes; other large multidimensional leaves can exceed its admitted limit.

## License

Original artifact code, generated cases, results, and documentation are available under the MIT License in `LICENSE`. No ACM class or bibliography-style file is included in this standalone repository.
