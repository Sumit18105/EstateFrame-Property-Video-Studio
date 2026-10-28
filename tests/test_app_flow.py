import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class AppFlowTests(unittest.TestCase):
    def test_entered_details_survive_step_changes(self):
        at = AppTest.from_file(APP, default_timeout=120).run()
        self.assertFalse(at.exception)
        next(b for b in at.button if b.key == "home_create_video").click().run()
        at.text_input(key="property_name").set_value("My Custom Home").run()
        at.text_input(key="location").set_value("Chandigarh").run()
        next(b for b in at.button if b.key == "details_next").click().run()
        next(b for b in at.button if b.key == "photos_next").click().run()
        self.assertEqual(at.session_state["property_name"], "My Custom Home")
        self.assertEqual(at.session_state["location"], "Chandigarh")
        self.assertIn("My Custom Home", at.session_state["voiceover_script"])
        self.assertFalse(at.exception)


if __name__ == "__main__":
    unittest.main()
