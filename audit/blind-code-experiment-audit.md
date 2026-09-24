# Blind code and experiment audit

Gate: **FAIL**

## Code volume
```json
{
  "production_python": {
    "files": 22,
    "total_lines": 2986,
    "nonblank_lines": 2579,
    "comment_lines": 28
  },
  "test_python": {
    "files": 1,
    "total_lines": 474,
    "nonblank_lines": 425,
    "comment_lines": 18
  },
  "shell": {
    "files": 1,
    "total_lines": 4,
    "nonblank_lines": 4,
    "comment_lines": 1
  },
  "latex": {
    "files": 1,
    "total_lines": 808,
    "nonblank_lines": 635,
    "comment_lines": 0
  }
}
```

## Reproduction and determinism
- Clean runs: [(1, 1.38), (1, 1.46)]
- Canonical files compared: 849
- Deterministic differences: 0

## Static audit
- Syntax errors: 0
- Production stubs: 0
- Placeholder markers: 52
- eval/exec calls: 0

## Holdout
- No qualifying holdout result located.

## Blocking findings
- pytest failed
- clean reproduction or determinism failed
- placeholder markers remain
- no independent prospective/holdout result found
