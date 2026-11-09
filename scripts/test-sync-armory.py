#!/usr/bin/env python3
"""Offline normalization tests; no Battle.net network requests or credentials."""
import importlib.util
import unittest

spec = importlib.util.spec_from_file_location("armory_sync", "scripts/sync-armory.py")
armory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(armory)


class ArmoryTests(unittest.TestCase):
    def test_maps_hand_and_primary_stats(self):
        gear = armory.normalize_equipment({"equipped_items": [{
            "slot": {"type": "HAND", "name": "Hands"},
            "name": "Test Gloves", "item": {"id": 12345},
            "armor": {"value": 42}, "stats": [
                {"type": {"type": "AGILITY", "name": "Agility"}, "value": 5},
                {"type": {"type": "STAMINA", "name": "Stamina"}, "value": 3},
                {"type": {"type": "INTELLECT", "name": "Intellect"}, "value": 7,
                 "is_negated": True}
            ], "spells": [{"description": "Equip: Test effect"}]
        }]})
        self.assertEqual(gear["Hands"]["stats"], {"Agility": 5, "Stamina": 3, "Intellect": 0})
        self.assertEqual(gear["Hands"]["armor"], 42)
        self.assertEqual(gear["Hands"]["effects"], ["Equip: Test effect"])

    def test_missing_armor_is_unknown(self):
        gear = armory.normalize_equipment({"equipped_items": [
            {"slot": {"type": "WRIST"}, "name": "Test Bracers", "item": {"id": 777}}
        ]})
        self.assertIsNone(gear["Wrist"]["armor"])

    def test_profession_tier(self):
        raw = {"primaries": [{"profession": {"name": "Leatherworking"},
                              "tiers": [{"skill_points": 190}, {"skill_points": 75}]}]}
        self.assertEqual(armory.find_skill(raw), 190)
        self.assertIsNone(armory.find_skill({}))


if __name__ == "__main__":
    unittest.main()
