"""Split invariants; runs without PyTorch or GPU."""
import unittest
from proteintalks_cell_holdout import split_conditions, cell_of


class SplitTests(unittest.TestCase):
    def setUp(self):
        self.names = [f"{cell}_#{drug}" for cell in ("MCF7", "MCF70", "BT20", "BT549") for drug in range(10)]

    def test_exact_cell_and_exhaustive_disjoint_split(self):
        split = split_conditions(self.names)
        self.assertEqual([len(split[k]) for k in ("train", "val", "test")], [24, 6, 10])
        flattened = sum(split.values(), [])
        self.assertEqual(sorted(flattened), list(range(40)))
        self.assertTrue(all(cell_of(self.names[i]) == "MCF7" for i in split["test"]))
        self.assertTrue(all(cell_of(self.names[i]) != "MCF7" for k in ("train", "val") for i in split[k]))

    def test_reproducible(self):
        self.assertEqual(split_conditions(self.names), split_conditions(self.names))
        self.assertNotEqual(split_conditions(self.names, seed=1)["train"], split_conditions(self.names, seed=2)["train"])

    def test_invalid_or_duplicate_input(self):
        for names, kwargs in [(self.names, {"holdout": "typo"}), (self.names, {"val_fraction": 0}),
                              (self.names + [self.names[0]], {})]:
            with self.assertRaises(ValueError):
                split_conditions(names, **kwargs)


if __name__ == "__main__":
    unittest.main()
