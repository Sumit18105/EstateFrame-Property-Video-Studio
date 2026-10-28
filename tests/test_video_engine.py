import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image

import imageio_ffmpeg
from video_engine import render_video


class VideoEngineTests(unittest.TestCase):
    def test_export_requires_four_to_eight_images(self):
        with self.assertRaisesRegex(ValueError, "Add 4–8 property images"):
            render_video([Image.new("RGB", (320, 240), "gray") for _ in range(3)], {}, Path("should_not_be_created.mp4"))

    def test_export_creates_playable_mp4_for_each_supported_format(self):
        images = [
            Image.new("RGB", (160, 120), color)
            for color in [(125, 48, 58), (70, 42, 38), (180, 140, 110), (44, 21, 18)]
        ]
        details = {
            "property_name": "Test Residence",
            "location": "Sample City",
            "property_type": "Apartment",
            "price": "",
            "key_features": ["Balcony"],
            "scene_captions": "Exterior\nLiving area\nKitchen\nBedroom",
            "cta": "Enquire today",
            "brand_name": "EstateFrame",
            "tone": "Architectural editorial",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            expected_resolutions = {
                "16:9 · Landscape": "512x288",
                "9:16 · Portrait": "288x512",
                "1:1 · Square": "432x432",
            }
            for fmt in expected_resolutions:
                path = Path(temp_dir) / (fmt.split()[0].replace(':', 'x') + ".mp4")
                result = render_video(
                    images=images,
                    details={**details, "aspect_ratio": fmt},
                    output_path=path,
                    aspect_ratio=fmt,
                    scene_seconds=1.5,
                    transition_seconds=0.15,
                    output_scale=0.4,
                )
                self.assertTrue(path.exists())
                self.assertGreater(path.stat().st_size, 1000)
                self.assertEqual(result["scene_count"], 6)  # cover + four photos + enquiry card
                self.assertGreater(result["duration_seconds"], 0)
                self.assertEqual(result["resolution"], expected_resolutions[fmt])

    def _probe(self, path):
        out = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
        h, m, sec = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
        return int(h) * 3600 + int(m) * 60 + float(sec), "Audio:" in out

    def _tone(self, path, seconds):
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi",
                        "-i", f"sine=frequency=440:duration={seconds}", str(path)], check=True)

    def test_audio_modes_and_long_narration_not_truncated(self):
        images = [Image.new("RGB", (160, 120), (90 + i * 20, 50, 60)) for i in range(4)]
        details = {"property_name": "Audio Test", "aspect_ratio": "16:9 · Landscape"}
        kwargs = dict(images=images, details=details, aspect_ratio="16:9 · Landscape",
                      scene_seconds=1.5, transition_seconds=0.15, output_scale=0.4)
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp = Path(temp_dir)
            voice, music = tmp / "voice.wav", tmp / "music.wav"
            self._tone(voice, 14)   # longer than the ~8 s slideshow
            self._tone(music, 3)
            silent = render_video(output_path=tmp / "a.mp4", **kwargs)
            self.assertFalse(self._probe(tmp / "a.mp4")[1])
            for name, extra in {"voice": {"voiceover_path": str(voice)}, "music": {"music_path": str(music)},
                                "both": {"voiceover_path": str(voice), "music_path": str(music)}}.items():
                result = render_video(output_path=tmp / f"{name}.mp4", **kwargs, **extra)
                duration, has_audio = self._probe(tmp / f"{name}.mp4")
                self.assertTrue(has_audio, name)
                if "voice" in extra.get("voiceover_path", "voice") and name != "music":
                    self.assertGreaterEqual(duration, 14.0, name)  # narration is not cut off
                else:
                    self.assertAlmostEqual(duration, silent["duration_seconds"], delta=0.3)


if __name__ == "__main__":
    unittest.main()
