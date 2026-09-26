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


if __name__ == "__main__":
    unittest.main()
