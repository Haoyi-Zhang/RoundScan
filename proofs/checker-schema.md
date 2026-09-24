# Ordered-cover certificate schema

Schema tag: `fixedscan-ordered-cover-1`.

A certificate embeds the complete instance, producer method, claimed status, consecutive output roots, and optional violation metadata. The checker treats every field as untrusted. The accepted language is a closed JSON schema: unknown fields are rejected; semantic integers must have exact JSON integer type (booleans, floats, and numeric strings are not integers); duplicate object keys and nonstandard `NaN`/`Infinity` constants are rejected.

A tree node has one of three kinds:

- `safe`: contains its exact traversal box, a vector of supplied difference bounds, and an informational proof label. The checker recomputes the exact range and verifies containment and tolerance.
- `witness`: must be a singleton box. The checker reconstructs the point, replays both executions, compares the supplied difference, and verifies a tolerance violation.
- `split`: contains the exact traversal box, the first nonsingleton coordinate, an interior cut, and a left child. A right child is required only after the left child is proven safe; it is forbidden after a left witness.

Canonical splitting makes every point in the left child lexicographically earlier than every point in the right child. Consecutive safe output roots establish temporal minimality. Unknown producer outcomes, malformed boxes, duplicate JSON keys, non-finite constants, unknown fields, wrong JSON types, mismatched embedded instances, noncanonical splits, loose unsafe bounds, and non-replaying witnesses are rejected.

The default admission limits are 16 MiB of JSON, 500,000 parsed tree nodes, and depth 512. Embedded and standalone instances are limited to width 2--32, scale at most 256 and below the positive signed endpoint, dimension 1--32, horizon 1--128, and chunk length 1--64. Earliest-output indices must lie inside the declared horizon. These are executable engineering limits, not assumptions hidden in the general hand proofs.
