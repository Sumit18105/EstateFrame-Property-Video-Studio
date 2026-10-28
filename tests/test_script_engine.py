import unittest
from script_engine import build_scene_plan, generate_script, parse_features


class ScriptEngineTests(unittest.TestCase):
    def test_features_are_cleaned_and_deduplicated(self):
        self.assertEqual(parse_features(" • Balcony \nBalcony\n  Modular kitchen "), ["Balcony", "Modular kitchen"])

    def test_features_accept_comma_separated_custom_values(self):
        self.assertEqual(parse_features("Garage, Patio; Balcony"), ["Garage", "Patio", "Balcony"])

    def test_script_only_uses_supplied_listing_facts(self):
        script = generate_script({"property_name": "Lotus House", "location": "Sector 1", "key_features": ["Private terrace"]})
        self.assertIn("Lotus House", script["voiceover"])
        self.assertIn("Sector 1", script["voiceover"])
        self.assertIn("Private terrace", script["voiceover"])
        self.assertNotIn("swimming pool", script["voiceover"].lower())
        self.assertNotIn("investment return", script["voiceover"].lower())

    def test_captions_map_by_image_index(self):
        plan = build_scene_plan({
            "property_name": "Test Home",
            "scene_captions": "Exterior\nKitchen\nBedroom\nBalcony",
        }, 4)
        photo_scenes = [scene for scene in plan if scene["kind"] == "feature"]
        self.assertEqual([scene["headline"] for scene in photo_scenes], ["Exterior", "Kitchen", "Bedroom", "Balcony"])
        self.assertEqual(len(plan), 6)  # cover + 4 photo scenes + outro


if __name__ == "__main__":
    unittest.main()
