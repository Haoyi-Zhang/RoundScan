"""Finite arithmetic-domain regressions; no campaign or performance measurement."""
from itertools import product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from fixedscan import arithmetic as producer
from fixedscan import checker_arithmetic as checker
from fixedscan.model import Box, Instance


def fixture(association='left', rounding='floor'):
    return Instance('trace-domain', 'finite-regression', 4, 2, rounding, 2, 3, 2,
                    association, (1, -1), (((2, 1), (-1, 2)),) * 3,
                    ((Box(-1, 1), Box(0, 1)),) * 3, ((0, 0),) * 3, {})


class TraceInputDomainTests(unittest.TestCase):
    def test_frozen_corpus_endpoint_traces_remain_equal(self):
        files = sorted((Path(__file__).resolve().parents[1] / 'cases' / 'frozen').glob('*.json'))
        self.assertEqual(len(files),72)
        for path in files:
            instance = Instance.load(path)
            for endpoint in ('lo','hi'):
                inputs = tuple(tuple(getattr(box,endpoint) for box in row) for row in instance.boxes)
                self.assertEqual(producer.sequential_trace(instance,inputs),
                                 checker.sequential_trace(instance,inputs))
                self.assertEqual(producer.lowered_trace(instance,inputs),
                                 checker.lowered_trace(instance,inputs))

    def test_both_paths_reject_each_outside_coordinate(self):
        instance = fixture()
        for step, coordinate, direction in product(range(3), range(2), (-1, 1)):
            rows = [[0, 0] for _ in range(3)]
            box = instance.boxes[step][coordinate]
            rows[step][coordinate] = box.lo - 1 if direction < 0 else box.hi + 1
            for module in (producer, checker):
                for function in (module.sequential_trace, module.lowered_trace):
                    with self.subTest(step=step, coordinate=coordinate, direction=direction,
                                      function=function.__module__ + '.' + function.__name__):
                        with self.assertRaisesRegex(ValueError, 'outside declared box'):
                            function(instance, rows)

    def test_legal_complete_traces_remain_equal_on_both_paths(self):
        rows = tuple(product(range(-1, 2), range(2)))
        for association, rounding in product(('left', 'right', 'balanced'), ('floor', 'rne')):
            instance = fixture(association, rounding)
            for inputs in product(rows, repeat=3):
                self.assertEqual(producer.sequential_trace(instance, inputs),
                                 checker.sequential_trace(instance, inputs))
                self.assertEqual(producer.lowered_trace(instance, inputs),
                                 checker.lowered_trace(instance, inputs))

    def test_type_horizon_and_dimension_rejections_remain(self):
        instance = fixture()
        for module in (producer, checker):
            for function in (module.sequential_trace, module.lowered_trace):
                for rows, error in (([(0, 0)], ValueError),
                                    ([(0,), (0, 0), (0, 0)], ValueError),
                                    ([(True, 0), (0, 0), (0, 0)], TypeError),
                                    ([(0.0, 0), (0, 0), (0, 0)], TypeError)):
                    with self.assertRaises(error):
                        function(instance, rows)


if __name__ == '__main__':
    unittest.main()
