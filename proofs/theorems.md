# Theorem and evidence index

The mathematical arguments are in `arguments.tex`. They are hand proofs, not a proof-assistant development. Line-level executable support is listed so that a reviewer can distinguish a general theorem from a finite check.

| ID | Statement | Maturity | Executable support | Important boundary |
|---|---|---|---|---|
| L1 | Floor residuals are periodic under translations by `q`; nearest-even residuals are periodic under `2q`, and `q` is unsound in general. | Proved; finite-checked | `transport.py`; `tests/run_all.py` (`translation_periods`, `rne_q_counterexamples`) | Unsaturated residual identity; clipping is not periodic. |
| L2 | The paired symbolic transformer encloses every concrete lowered-minus-reference output on its input subbox. | Proved; finite-checked | `symbolic.py`; exhaustive development/frozen comparisons (`sound_enclosures`) | Sound overapproximation only; no completeness or general polynomial-time claim. |
| L3 | The scalar checker dynamic program computes exact ranges while respecting left, right, and balanced association. | Proved; finite-checked | `exact_box.py`; 48 DP/exhaustive output comparisons | Large nonscalar leaves outside the enumeration limit are rejected. |
| T1 | An accepted safe ordered-cover certificate proves every-output safety; an accepted violation certificate proves earliest output and lexicographically first prefix. | Proved; finite-checked and mutation-tested | `checker.py`; 334 accepted certificates; 35 semantic mutations plus 18 parser/admission/model/API attacks rejected | Depends on exact admitted leaves and the embedded finite semantics. |
| T2 | Without node/time cutoffs, canonical subdivision is complete for finite boxes. | Proved | `producer.py` structure; singleton replay tests | Resource-bounded runs may return `unknown`, which is not a proof. |
| T3 | Local same-carry error bounds compose through chunks using the exact integer rounding modulus. | Proved | `transport.py` checks the scalar modulus; running examples in tests | Conditional on valid local contracts and a carry set containing both actual carries. |
| T4 | Common block-diagonal structure gives exact execution factorization, safety equivalence, earliest-time minimum, and ordered witness lifting. | Proved; finite-checked | `blocks.py`; 4,914 prefix vectors and 4 lifted witnesses | Requires a Cartesian input domain and the same block partition at every step. |
| T5 | Universal zero-error safety is coNP-complete with signed three-bit words and two-step chunks when dimension/horizon grow. | Proved; bounded construction families exhaustively checked | `reductions.py::compile_circuit`; 832 assignment/mode executions | General hardness proof is by reduction; executable tests exhaust the declared one- and two-gate families plus the running three-gate case. |
| T6 | Final-output safety is coNP-complete with five state coordinates when width/horizon grow. | Proved; bounded construction families exhaustively checked | `reductions.py::compile_packed_cnf`; 867 formulas and 6,474 assignment executions | Scale two, floor rounding, one nonvacuous final coordinate; the executable family includes empty, duplicate-literal, and tautological clauses. |
| C1 | Universal polynomial-size, polynomial-time-checkable safety certificates for either hard family would imply NP = coNP. | Proved conditional corollary | Follows from T5/T6 | A complexity-theoretic obstruction, not a claim that small certificates never occur. |

## Recorded finite evidence

`results/test-summary.json` is the machine-readable test ledger. `results/frozen-summary.json` and `results/stress-summary.json` are the campaign summaries. `claim_evidence_ledger.csv` maps paper-level claims to the exact files and result rows used.
