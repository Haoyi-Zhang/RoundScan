# Experiment design

## Frozen semantic suite

The frozen suite is a deterministic, generated semantic test collection, not a workload benchmark. Its 72 cases were generated with seed 90173 before campaign outcomes were inspected. It contains 18 instances in each of four structural families: scalar stable-coefficient, scalar unstable-coefficient, diagonal, and coupled. Scalar horizons are four and two-coordinate horizons are three. Scales, widths, rounding modes, chunk lengths, association trees, saturation exposure, and tolerance construction vary deterministically. Every varying input coordinate has three values, enabling an exhaustive prefix oracle. Tolerances are derived from oracle maxima either at the exact safe maximum or one code below the first positive maximum, yielding 33 safe and 39 violated cases without dropping unfavorable instances.

The compared methods are independent interval covers; paired covers with fresh residuals, syntactic residual sharing, and modular residual sharing; and an exact finite-state dynamic program. Each cover producer receives the same 5,000-node and 20-second internal limits on the frozen suite. The checker is outside the production budget.

## Long-horizon stress suite

The stress suite contains 16 scalar cases at horizons 8, 16, 32, and 64, crossing two coefficient regimes and both rounding modes. All contracts are safe. Cover methods receive 20,000 nodes and five internal seconds; exact DP receives 12 seconds. `unknown` is retained in every denominator. These cases probe resource-bound behavior only; they do not establish model or deployment scalability.

## Negative controls and mutations

Tests include an invalid one-scale nearest-even translation period, attempted periodic saturation, and contraction-style reasoning that would be unsound for the declared integer map. Certificate mutations alter semantic bindings, omit required roots or children, corrupt ordered splitting, alter witnesses or first times, forge safe ranges, and exploit JSON Boolean/integer equality. Duplicate JSON keys are rejected.

## Measurement interpretation

Claim-bearing values are statuses, accepted/rejected checks, deterministic node counts for completed searches, and exact oracle comparisons. CPU times and peak RSS describe this Python implementation and host only. They are not hardware speedups, asymptotic bounds, or bit-identical reproduction targets.
