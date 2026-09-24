#!/usr/bin/env python3
"""Self-contained scientific and artifact regression suite."""
from __future__ import annotations

import copy
import csv
import json
import tempfile
from collections import Counter
from dataclasses import replace
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fixedscan.arithmetic import (
    lowered_trace as producer_lowered,
    output_difference as producer_difference,
    round_div as producer_round,
    sequential_trace as producer_sequential,
)
from fixedscan.baseline import exact_baseline
from fixedscan.blocks import project_coordinate, project_prefix
from fixedscan.checker import check, load_and_check, load_instance_file
from fixedscan.checker_arithmetic import (
    lowered_trace as checker_lowered,
    output_difference as checker_difference,
    round_div as checker_round,
    sequential_trace as checker_sequential,
)
from fixedscan.exact_box import scalar_full_prefix_ranges
from fixedscan.interval_analysis import independent_bounds
from fixedscan.model import Box, Instance
from fixedscan.oracle import exact_oracle
from fixedscan.reductions import (
    Gate, P, circuit_inputs, cnf_value, compile_circuit, compile_packed_cnf,
    evaluate_circuit, packed_inputs,
)
from fixedscan.symbolic import paired_bounds
from fixedscan.transport import nearest_even_scale_counterexample, residual, verify_translation


COUNTS: dict[str, int] = {}


def record(name: str, count: int = 1) -> None:
    COUNTS[name] = COUNTS.get(name, 0) + count


def load_cases(split: str) -> list[Instance]:
    return [Instance.load(p) for p in sorted((ROOT / "cases" / split).glob("*.json"))]


def test_rounding() -> None:
    for q in (2, 4, 8, 16):
        for mode in ("floor", "rne"):
            for n in range(-8 * q, 8 * q + 1):
                assert producer_round(n, q, mode) == checker_round(n, q, mode)
                record("rounding_values")
            assert verify_translation(q, mode)
            record("translation_periods")
        a, b = nearest_even_scale_counterexample(q)
        assert b - a == q and residual(a, q, "rne") != residual(b, q, "rne")
        record("rne_q_counterexamples")


def all_prefix_points(instance: Instance, t: int):
    return product(*(box.values() for box in instance.prefix_boxes(t)))


def test_paths_and_analyzers() -> None:
    prefix_evaluations = 0
    for split in ("development", "frozen"):
        for instance in load_cases(split):
            oracle = exact_oracle(instance)
            prefix_evaluations += oracle.prefix_evaluations
            if split == "frozen":
                assert oracle.safe == bool(instance.metadata["oracle_safe"])
                assert oracle.earliest_output == instance.metadata["oracle_earliest_output"]
                stored = instance.metadata["oracle_witness"]
                assert oracle.witness == (tuple(stored) if stored is not None else None)
            for t, exact_row in enumerate(oracle.ranges):
                boxes = instance.prefix_boxes(t)
                independent = independent_bounds(instance, t, boxes)
                analyses = [tuple((x.lo, x.hi) for x in independent)]
                for policy in ("fresh", "syntactic", "residue"):
                    analyses.append(tuple((x.lo, x.hi) for x in paired_bounds(instance, t, boxes, policy)))
                for bounds in analyses:
                    for (elo, ehi), (lo, hi) in zip(exact_row, bounds):
                        assert lo <= elo <= ehi <= hi
                        record("sound_enclosures")
            for t in range(instance.horizon):
                for point in all_prefix_points(instance, t):
                    assert producer_difference(instance, point, t) == checker_difference(instance, point, t)
                    record("cross_path_prefixes")
    assert prefix_evaluations == 11268 + 33804
    record("oracle_prefix_evaluations", prefix_evaluations)


def test_association_dp_regression() -> None:
    base = Instance.load(ROOT / "cases" / "stress" / "stress-000.json")
    for association in ("left", "right", "balanced"):
        for mode in ("floor", "rne"):
            instance = replace(base, association=association, rounding=mode)
            ranges = scalar_full_prefix_ranges(instance)
            for t in range(8):
                values = [producer_difference(instance, p, t)[0] for p in all_prefix_points(instance, t)]
                assert ranges[t] == (min(values), max(values))
                record("dp_exhaustive_outputs")


def _nodes(node: dict):
    yield node
    if node.get("kind") == "split":
        yield from _nodes(node["left"])
        if "right" in node:
            yield from _nodes(node["right"])


def _first_kind(certificate: dict, kind: str) -> dict:
    for root in certificate["roots"]:
        for node in _nodes(root["tree"]):
            if node.get("kind") == kind:
                return node
    raise AssertionError(f"no {kind} node")


def test_certificates_and_mutations() -> None:
    accepted = 0
    for split in ("frozen", "stress"):
        cases = {x.name: x for x in load_cases(split)}
        for path in sorted((ROOT / "results" / "certificates" / split).glob("*.json")):
            name = path.name.rsplit("-", 1)[0]
            # Method names contain a hyphen only for exact-dp, which never has a certificate.
            for suffix in ("-interval.json", "-fresh.json", "-syntactic.json", "-residue.json"):
                if path.name.endswith(suffix):
                    name = path.name[:-len(suffix)]
                    break
            result = load_and_check(path, cases[name])
            assert result["accepted"], (path, result)
            accepted += 1
    assert accepted == 334
    record("accepted_certificates", accepted)

    safe_path = ROOT / "results" / "certificates" / "frozen" / "case-000-interval.json"
    bad_path = ROOT / "results" / "certificates" / "frozen" / "case-001-fresh.json"
    safe = json.loads(safe_path.read_text())
    bad = json.loads(bad_path.read_text())
    mutations: list[tuple[str, dict]] = []

    def mutate(label: str, value: dict) -> None:
        mutations.append((label, value))

    x = copy.deepcopy(safe); x["schema"] = "wrong"; mutate("wrong schema", x)
    x = copy.deepcopy(safe); x["instance"]["dimension"] += 1; mutate("dimension mismatch", x)
    x = copy.deepcopy(safe); x["roots"][0]["output"] = 1; mutate("nonconsecutive output", x)
    x = copy.deepcopy(safe); x["roots"] = x["roots"][:-1]; mutate("missing root", x)
    x = copy.deepcopy(safe); _first_kind(x, "safe")["bounds"][0] = [999, 999]; mutate("forged safe bound", x)
    x = copy.deepcopy(safe); node = _first_kind(x, "split"); node["coordinate"] += 1; mutate("noncanonical split", x)
    x = copy.deepcopy(safe); node = _first_kind(x, "split"); node["cut"] = node["box"][node["coordinate"]][0] - 1; mutate("exterior cut", x)
    x = copy.deepcopy(safe); node = _first_kind(x, "split"); node.pop("right", None); mutate("missing right child", x)
    x = copy.deepcopy(bad); _first_kind(x, "witness")["point"][0] += 1; mutate("forged witness point", x)
    x = copy.deepcopy(bad); _first_kind(x, "witness")["difference"][0] += 1; mutate("forged witness difference", x)
    x = copy.deepcopy(bad); x["witness"][0] += 1; mutate("top-level witness mismatch", x)
    x = copy.deepcopy(bad); x["earliest_output"] -= 1; mutate("earliest output mismatch", x)
    x = copy.deepcopy(bad); x["status"] = "safe"; mutate("violation relabeled safe", x)
    x = copy.deepcopy(safe); x["status"] = "unknown"; mutate("unknown is not proof", x)
    x = copy.deepcopy(safe); x["roots"][0]["tree"]["box"][0][0] += 1; mutate("traversal box mismatch", x)

    # Exact JSON typing is part of the admitted certificate language.  These
    # values were accepted by the former int(...) coercions despite not being
    # JSON integers of the declared schema.
    x = copy.deepcopy(safe); x["instance"]["dimension"] = True; mutate("boolean dimension", x)
    x = copy.deepcopy(safe); x["instance"]["width"] = str(x["instance"]["width"]); mutate("string width", x)
    x = copy.deepcopy(safe); x["instance"]["matrices"][0][0][0] = float(x["instance"]["matrices"][0][0][0]); mutate("float coefficient", x)
    x = copy.deepcopy(safe); node = _first_kind(x, "safe"); node["bounds"][0][0] = str(node["bounds"][0][0]); mutate("string safe bound", x)
    x = copy.deepcopy(safe); node = _first_kind(x, "split"); node["coordinate"] = False; mutate("boolean split coordinate", x)
    x = copy.deepcopy(safe); node = _first_kind(x, "split"); node["cut"] = float(node["cut"]); mutate("float split cut", x)
    x = copy.deepcopy(bad); node = _first_kind(x, "witness"); node["point"][0] = str(node["point"][0]); mutate("string witness point", x)
    x = copy.deepcopy(bad); x["earliest_output"] = float(x["earliest_output"]); mutate("float earliest output", x)
    x = copy.deepcopy(safe); x["roots"][0]["output"] = False; mutate("boolean root output", x)
    x = copy.deepcopy(safe); x["unexpected"] = 1; mutate("unknown certificate field", x)
    x = copy.deepcopy(safe); _first_kind(x, "safe")["unexpected"] = 1; mutate("unknown node field", x)
    x = copy.deepcopy(safe); x["method"] = 7; mutate("non-string method", x)
    x = copy.deepcopy(safe); x["diagnostics"] = []; mutate("non-object diagnostics", x)

    # Claimed implementation limits and earliest-output range are enforced by
    # the checker before allocating shapes or traversing roots.
    x = copy.deepcopy(bad); x["earliest_output"] = -1; mutate("negative earliest output", x)
    x = copy.deepcopy(bad); x["earliest_output"] = x["instance"]["horizon"]; mutate("earliest output beyond horizon", x)
    x = copy.deepcopy(safe); x["instance"]["width"] = 33; mutate("width over checker limit", x)
    x = copy.deepcopy(safe); x["instance"]["width"] = 16; x["instance"]["scale"] = 512; mutate("scale over checker limit", x)
    x = copy.deepcopy(safe); x["instance"]["dimension"] = 33; mutate("dimension over checker limit", x)
    x = copy.deepcopy(safe); x["instance"]["horizon"] = 129; mutate("horizon over checker limit", x)
    x = copy.deepcopy(safe); x["instance"]["chunk_length"] = 65; mutate("chunk over checker limit", x)

    for label, mutation in mutations:
        result = check(mutation)
        assert not result["accepted"], (label, result)
        record("rejected_mutations")

    with tempfile.TemporaryDirectory() as tmp:
        duplicate = Path(tmp) / "duplicate.json"
        duplicate.write_text('{"schema":"fixedscan-ordered-cover-1","schema":"duplicate"}', encoding="utf-8")
        result = load_and_check(duplicate)
        assert not result["accepted"] and "duplicate" in result["error"]
        record("rejected_duplicate_keys")

        for constant in ("NaN", "Infinity"):
            nonfinite = Path(tmp) / f"nonfinite-{constant}.json"
            nonfinite.write_text(
                '{"schema":"fixedscan-ordered-cover-1","diagnostics":{"x":' + constant + '}}',
                encoding="utf-8",
            )
            result = load_and_check(nonfinite)
            assert not result["accepted"] and "non-standard JSON constant" in result["error"]
            record("rejected_nonfinite_constants")

        result = load_and_check(safe_path, max_bytes=16)
        assert not result["accepted"] and "input-size limit" in result["error"]
        record("rejected_admission_limits")
        result = load_and_check(safe_path, max_nodes=1)
        assert not result["accepted"] and "node limit" in result["error"]
        record("rejected_admission_limits")
        result = load_and_check(safe_path, max_depth=1)
        assert not result["accepted"] and "depth limit" in result["error"]
        record("rejected_admission_limits")
        result = check(safe, max_nodes=True)
        assert not result["accepted"] and "max_nodes" in result["error"]
        record("rejected_admission_limits")

        # Independent instance files use the same strict parser as embedded
        # instances, including duplicate-key and non-finite rejection.
        base_instance = safe["instance"]
        files = {
            "duplicate-instance.json": '{"name":"a","name":"b"}',
            "nonfinite-instance.json": '{"name":"a","width":NaN}',
            "boolean-instance.json": json.dumps({**base_instance, "width": True}),
            "unknown-field-instance.json": json.dumps({**base_instance, "extra": 1}),
        }
        for filename, payload in files.items():
            path = Path(tmp) / filename
            path.write_text(payload, encoding="utf-8")
            try:
                load_instance_file(path)
            except (TypeError, ValueError):
                record("rejected_instance_files")
            else:
                raise AssertionError(f"strict instance loader accepted {filename}")

    base_dict = Instance.load(ROOT / "cases" / "development" / "dev-000.json").to_dict()
    for mutation in (
        {**base_dict, "width": True},
        {**base_dict, "h0": [str(x) for x in base_dict["h0"]]},
        {**base_dict, "unexpected": 1},
    ):
        try:
            Instance.from_dict(mutation)
        except (TypeError, ValueError):
            record("rejected_strict_model_values")
        else:
            raise AssertionError("strict model parser accepted a malformed instance")

    instance = Instance.load(ROOT / "cases" / "development" / "dev-000.json")
    valid_prefix = tuple(box.lo for box in instance.prefix_boxes(0))
    bad_calls = (
        lambda: producer_difference(instance, (True,) + valid_prefix[1:], 0),
        lambda: checker_difference(instance, (float(valid_prefix[0]),) + valid_prefix[1:], 0),
        lambda: circuit_inputs(compile_circuit(1, [], 0, "floor"), ("0",)),
        lambda: packed_inputs(compile_packed_cnf(1, tuple()), True),
    )
    for call in bad_calls:
        try:
            call()
        except (TypeError, ValueError):
            record("rejected_noninteger_inputs")
        else:
            raise AssertionError("non-integer public input was accepted")


def test_block_factorization() -> None:
    cases = [x for x in load_cases("frozen") if x.family == "diagonal"][:6]
    assert len(cases) == 6
    total = 0
    for instance in cases:
        projections = [project_coordinate(instance, i) for i in range(instance.dimension)]
        for t in range(instance.horizon):
            for point in all_prefix_points(instance, t):
                full = producer_difference(instance, point, t)
                for i, projection in enumerate(projections):
                    pp = project_prefix(tuple(point), instance.dimension, i)
                    assert full[i] == producer_difference(projection, pp, t)[0]
                total += 1
        global_oracle = exact_oracle(instance)
        block_oracles = [exact_oracle(p) for p in projections]
        earliest = min((o.earliest_output for o in block_oracles if o.earliest_output is not None), default=None)
        assert earliest == global_oracle.earliest_output
        if earliest is not None:
            candidates = []
            for i, oracle in enumerate(block_oracles):
                if oracle.earliest_output != earliest:
                    continue
                assert oracle.witness is not None
                lifted = []
                for t in range(earliest + 1):
                    for j in range(instance.dimension):
                        lifted.append(oracle.witness[t] if i == j else instance.boxes[t][j].lo)
                candidates.append(tuple(lifted))
            assert min(candidates) == global_oracle.witness
            record("block_witness_lifts")
    assert total == 6 * (9 + 81 + 729)
    record("block_prefix_vectors", total)


def test_reductions() -> None:
    # Exhaust all one-gate circuits over three inputs and all two-gate circuits
    # over two inputs, including repeated AND operands.  Add the three-gate
    # running example and direct-input outputs.  This exercises both rounding
    # modes, every Boolean assignment, and every gate/register shape in these
    # bounded families.
    circuit_families: list[tuple[int, list[Gate], int]] = []
    for output in range(3):
        circuit_families.append((3, [], output))
    for kind in ("not", "and"):
        if kind == "not":
            for left in range(3):
                circuit_families.append((3, [Gate(kind, left)], 3))
        else:
            for left in range(3):
                for right in range(3):
                    circuit_families.append((3, [Gate(kind, left, right)], 3))
    first_gates = [Gate("not", left) for left in range(2)] + [
        Gate("and", left, right) for left in range(2) for right in range(2)
    ]
    second_gates = [Gate("not", left) for left in range(3)] + [
        Gate("and", left, right) for left in range(3) for right in range(3)
    ]
    for first in first_gates:
        for second in second_gates:
            circuit_families.append((2, [first, second], 3))
    circuit_families.append((3, [Gate("not", 1), Gate("and", 0, 3), Gate("and", 4, 2)], 5))

    fixed_checked = 0
    for num_inputs, gates, output in circuit_families:
        for mode in ("floor", "rne"):
            instance = compile_circuit(num_inputs, gates, output, mode)
            for assignment in product((0, 1), repeat=num_inputs):
                inputs = circuit_inputs(instance, assignment)
                reference = producer_sequential(instance, inputs)
                lowered = producer_lowered(instance, inputs)
                expected = evaluate_circuit(assignment, gates)[output]
                assert reference[-1][output] == expected
                assert lowered[-1][output] == 0
                assert all(reference[t] == lowered[t] for t in range(instance.horizon - 1))
                lo, hi = instance.word_bounds
                assert all(lo <= value <= hi for row in reference + lowered for value in row)
                fixed_checked += 1
    assert fixed_checked == 832
    record("fixed_width_assignments", fixed_checked)

    # Canonical clauses choose each variable absent, positive, or negative;
    # include the empty clause.  Exhaust every CNF with zero, one, or two such
    # clauses for one through three variables, then add duplicate-literal and
    # tautological clauses that canonical generation intentionally omits.
    packed_checked = 0
    packed_formulas = 0
    for variables in (1, 2, 3):
        clauses = []
        for signs in product((-1, 0, 1), repeat=variables):
            clause = tuple((i + 1) * sign for i, sign in enumerate(signs) if sign)
            clauses.append(clause)
        formulas: list[tuple[tuple[int, ...], ...]] = [tuple()]
        formulas.extend((clause,) for clause in clauses)
        formulas.extend((left, right) for left in clauses for right in clauses)
        formulas.extend([
            ((1, -1),),
            ((1, 1),),
        ])
        for formula in formulas:
            instance = compile_packed_cnf(variables, formula)
            packed_formulas += 1
            for code in range(1 << variables):
                inputs = packed_inputs(instance, code)
                reference = producer_sequential(instance, inputs)
                lowered = producer_lowered(instance, inputs)
                expected = cnf_value(code, variables, formula)
                assert reference[-1][P] == expected
                assert lowered[-1][P] == 0
                lo, hi = instance.word_bounds
                assert all(lo <= value <= hi for row in reference + lowered for value in row)
                packed_checked += 1
    assert packed_formulas == 867
    assert packed_checked == 6474
    record("packed_formulas", packed_formulas)
    record("packed_assignments", packed_checked)


def test_recorded_results() -> None:
    expected = {
        "frozen": {
            "interval": {"safe": 33, "violated": 39, "unknown": 0},
            "fresh": {"safe": 33, "violated": 39, "unknown": 0},
            "syntactic": {"safe": 33, "violated": 39, "unknown": 0},
            "residue": {"safe": 33, "violated": 39, "unknown": 0},
            "exact-dp": {"safe": 33, "violated": 39, "unknown": 0},
        },
        "stress": {
            "interval": {"safe": 10, "violated": 0, "unknown": 6},
            "fresh": {"safe": 12, "violated": 0, "unknown": 4},
            "syntactic": {"safe": 12, "violated": 0, "unknown": 4},
            "residue": {"safe": 12, "violated": 0, "unknown": 4},
            "exact-dp": {"safe": 16, "violated": 0, "unknown": 0},
        },
    }
    for split, by_method in expected.items():
        rows = list(csv.DictReader((ROOT / "results" / f"{split}-metrics.csv").open()))
        assert len(rows) == (360 if split == "frozen" else 80)
        for method, counts in by_method.items():
            got = Counter(r["status"] for r in rows if r["method"] == method)
            assert {k: got.get(k, 0) for k in counts} == counts
            record("result_method_summaries")
    frozen_rows = list(csv.DictReader((ROOT / "results" / "frozen-metrics.csv").open()))
    nodes = {m: sum(int(r["nodes"] or 0) for r in frozen_rows if r["method"] == m)
             for m in ("interval", "fresh", "syntactic", "residue")}
    assert nodes == {"interval": 24774, "fresh": 3260, "syntactic": 3260, "residue": 3260}
    record("frozen_node_totals")



def test_reference_inventory() -> None:
    """Keep the shipped scholarly provenance ledger closed and non-placeholder."""
    path = ROOT / "reference-audit.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 30
    keys: set[str] = set()
    identifiers: set[str] = set()
    for row in rows:
        key = row["bib_key"].strip()
        assert key and key not in keys
        keys.add(key)
        assert row["paper_cited"] == "yes"
        assert row["status"] == "verified"
        assert row["metadata_check"].strip()
        assert row["content_check"].strip()
        url = row["canonical_record"].strip()
        assert url.startswith("https://") and " " not in url
        identifier = (row["doi"].strip() or url).casefold().rstrip("/")
        assert identifier and identifier not in identifiers
        identifiers.add(identifier)
        payload = " ".join(row.values()).casefold()
        assert not any(token in payload for token in ("example.com", "placeholder", "todo", "tbd", "dummy"))
    record("verified_references", len(rows))

def main() -> int:
    test_rounding()
    test_paths_and_analyzers()
    test_association_dp_regression()
    test_certificates_and_mutations()
    test_block_factorization()
    test_reductions()
    test_recorded_results()
    test_reference_inventory()
    output = {"status": "PASS", "checks": COUNTS, "total_assertion_units": sum(COUNTS.values())}
    out_path = ROOT / "results" / "test-summary.json"
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
