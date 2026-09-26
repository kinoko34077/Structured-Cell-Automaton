import unittest
from types import SimpleNamespace

import core.memory_zone as memory_zone_module
from core.memory_zone import MemoryZone


class GenerationPruningContractTests(unittest.TestCase):
    def test_generation_pruning_policy_is_factored_and_configurable(self):
        self.assertEqual(
            getattr(memory_zone_module, "DEFAULT_MAX_AGE_GENERATIONS", None),
            60,
        )
        helper = getattr(memory_zone_module, "prune_memory_by_generation", None)
        self.assertTrue(callable(helper), "generation pruning helper is missing")

        zone = MemoryZone()
        old = SimpleNamespace(sid="old", tags=["old"], score=1.0)
        fresh = SimpleNamespace(sid="fresh", tags=["fresh"], score=1.0)
        zone.store(old, current_gen=0)
        zone.store(fresh, current_gen=50)

        helper(zone, current_generation=61)

        self.assertNotIn("old", zone.pool)
        self.assertIn("fresh", zone.pool)

    def test_pruning_methods_report_removed_count(self):
        zone = MemoryZone()
        low = SimpleNamespace(sid="low", tags=["low"], score=0.1)
        high = SimpleNamespace(sid="high", tags=["high"], score=0.9)
        zone.store(low, current_gen=0)
        zone.store(high, current_gen=50)

        self.assertEqual(zone.prune_by_score(min_score=0.3), 1)
        self.assertEqual(zone.prune_by_generation(current_gen=111, max_age=60), 1)

        empty = MemoryZone()
        self.assertEqual(empty.prune_by_score(min_score=0.3), 0)
        self.assertEqual(empty.prune_by_generation(current_gen=1, max_age=60), 0)
        self.assertEqual(empty.prune_by_similarity(threshold=0.9), 0)


if __name__ == "__main__":
    unittest.main()
