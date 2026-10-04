# Compositional Rounding Certificates

This repository is the standalone artifact for *Compositional Rounding Certificates for Chunked Affine Scans*. It specifies a bounded integer fixed-point recurrence, a declared chunk-prefix lowering, proof-producing ordered input covers, and an exact checker. The implementation has no third-party Python dependency.

## What is checked

An instance embeds signed word width, power-of-two scale, floor or round-to-nearest-even rounding, saturation, initial state, time-varying affine matrices, Cartesian input boxes, chunk length, association rule, and one tolerance vector per output. The reference executes every recurrence update. The lowering quantizes affine transfer summaries and evaluates every causal prefix from the same incoming chunk carry.

A conclusive ordered-cover certificate contains one root per proven-safe output and, when the contract fails, a singleton witness at the first failing output. The checker recomputes exact leaf ranges. It also enforces canonical first-nonsingleton splitting and left-before-right traversal, so an accepted violation certificate establishes the lexicographically first violating prefix at the earliest failing output. An `unknown` producer result is never accepted as a proof.

The producer closes an abstractly safe leaf only when the current exact checker admits that leaf: every scalar leaf has an exact finite-state DP path, while a multidimensional leaf must contain at most 100,000 points for complete enumeration. Otherwise the producer subdivides canonically and returns `unknown` if its node or time budget expires. This shared admission predicate contains no arithmetic fact; the checker still independently recomputes the exact range, and the unsplit 100,489-point root remains rejected even when supplied with truthful-looking bounds.

## Repository map

- `src/fixedscan/`: concrete semantics, analyses, producer, checker, exact baseline, leaf admission, transport recurrences, clipping instrumentation, block projection, and executable reduction constructions.
- `cases/`: deterministic development, frozen, and long-horizon stress instances.
- `results/raw/`: one authoritative raw record per instance and method.
- `results/certificates/`: all conclusive ordered-cover certificates.
- `results/*-metrics.csv`, `results/*-summary.json`, and `results/stress-by-horizon.csv`: derived campaign tables.
- `results/paper-results.tex`: manuscript rows generated from the same raw records and stored certificate files.
- `tests/run_all.py`: arithmetic cross-checks, exact-oracle comparisons, certificate and mutation checks, reduction checks, leaf-admission checks, transport checks, and result reconciliation.
- `proofs/`: hand proofs and claim-level statement index. These are not a mechanized formalization.
- `docs/validation-contract.md`: requirement-to-test map for the repaired acceptance boundary.
- `claim_evidence_ledger.csv`: paper claim to theorem, implementation, and result mapping.
- `reference-audit.csv`: one provenance row for every manuscript reference.
- `external_resources.csv`: scholarly/software resources and acquisition notes.

## Reproduce the checked evidence

Python 3.11 or newer is sufficient.

```sh
./reproduce.sh
```

The default path regenerates all deterministic case files in a temporary directory and compares them byte-for-byte, rebuilds every result table from the raw records, verifies recorded certificate byte counts against the actual files, audits the 30-entry scholarly-reference inventory, independently checks every stored certificate, reruns all finite oracles and mutation tests, and writes `results/reproduction.json`. It deliberately does not overwrite recorded wall/CPU timings.

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

The frozen suite contains 72 instances and 33,804 exact prefix evaluations. All frozen cases use chunk length two. The left, balanced, and right labels occur 24 times each, but a two-element chunk has only one binary composition tree; those labels are not nontrivial tree-shape evidence. Association-sensitive coverage instead comes from the separate eight-step scalar regression with 48 exact DP-versus-enumeration output comparisons. The inherited `stable` family is a lower-gain label, not a strict contraction condition: five of its 18 cases contain at least one unit-gain step.

All five methods classify the same 33 safe and 39 violating frozen instances. The four cover producers yield 288 certificates, all accepted by the checker. Independent interval covers use 24,774 nodes; each paired policy uses 3,260. The three paired residual-sharing policies therefore have identical final cover topology on this suite.

The raw-record-derived frozen totals are:

| Method | Nodes | Certificate bytes | Producer CPU (s) | Checker CPU (s) |
|---|---:|---:|---:|---:|
| Independent intervals | 24,774 | 2,583,453 | 1.557 | 0.598 |
| Fresh residuals | 3,260 | 384,903 | 4.182 | 0.374 |
| Syntactic sharing | 3,260 | 385,230 | 4.099 | 0.381 |
| Modular sharing | 3,260 | 385,082 | 4.100 | 0.385 |
| Exact finite-state DP | - | - | 0.353 | - |

The 16 stress instances have horizons 8, 16, 32, and 64. Exact finite-state dynamic programming resolves 16/16; paired covers resolve 12/16; independent interval covers resolve 10/16. Unresolved cases remain `unknown` rather than being counted as safe. `results/stress-by-horizon.csv` is regenerated from the raw records; for example, the horizon-eight fresh row contains 2,083 nodes.

The test suite records 188,847 assertion units. It includes 45,072 producer/checker concrete-prefix cross-checks, 45,072 exact-oracle prefix evaluations, 334 accepted stored certificates, 57 rejected mutation/parser/admission inputs, twelve leaf-admission closure/rejection/budget checks, 48 dynamic-program/exhaustive association checks, 4,914 block-factorization prefix checks and four lifted witnesses, 258 exact rounding-modulus comparisons, 73,572 carry-bound checks, 832 fixed-width circuit assignment/mode executions, 867 packed-CNF formulas over 6,474 assignments, 11,320,776 recorded pre-clip values across 7,306 reduction executions, and 30 audited scholarly-reference records. The reduction traces contain no clipping; a separate negative control activates clipping at sequential-state, summary-matrix, summary-bias, and carry-application sites.

## Trusted boundary and limitations

The checker accepts a closed JSON schema: semantic integers must be JSON integers (not booleans, floats, or strings), duplicate keys and nonstandard numeric constants are rejected, and explicit byte/node/depth plus model-size limits are enforced. It uses a separately written concrete-integer interpreter plus complete multidimensional enumeration or exact scalar DP. It does not use the producer's numbered-atom abstraction to discharge a leaf. The producer and checker share the structural leaf-admission predicate solely to avoid producing leaves the checker cannot replay.

The checker remains code produced and reviewed within one development process, not an independently authored or machine-verified checker. General theorem arguments in `proofs/arguments.tex` are hand proofs. Finite tests validate implemented cases but do not mechanize those general arguments. The generated suites are discriminating semantic and certificate tests, not trained-model, accelerator, deployment, or workload-performance evidence. Input boxes are Cartesian; one scale and rounding mode apply per instance; other large multidimensional leaves can exceed the exact checker's admitted limit and force subdivision or `unknown`.

## License

Original artifact code, generated cases, results, and documentation are available under the MIT License in `LICENSE`. No ACM class or bibliography-style file is included in this standalone repository.
