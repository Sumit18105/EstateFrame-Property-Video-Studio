"""Render a property film with Pillow frames and the bundled imageio-ffmpeg binary."""
from __future__ import annotations

import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import imageio_ffmpeg

from script_engine import build_scene_plan, generate_script

FPS = 24

PALETTES = {
    "Architectural editorial": {"accent": (139, 45, 58), "cream": (255, 255, 255), "ink": (44, 21, 18)},
    "Warm & welcoming": {"accent": (180, 78, 91), "cream": (255, 248, 245), "ink": (55, 33, 30)},
    "Clean minimal": {"accent": (164, 82, 94), "cream": (255, 255, 255), "ink": (44, 21, 18)},
    "High contrast": {"accent": (139, 45, 58), "cream": (255, 255, 255), "ink": (26, 12, 12)},
}


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if os.name == "nt":
        candidates.extend([r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"])
    candidates.extend([
        "/usr/share/fonts/truetype/lato/Lato-Bold.ttf" if bold else "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "arial.ttf",
    ])
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except (OSError, AttributeError):
            continue
    return ImageFont.load_default()


def _audio_duration(ffmpeg: str, path: str) -> float:
    """Return an audio file's duration in seconds (0.0 if it cannot be determined)."""
    try:
        result = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True, text=True, timeout=30)
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
        if match:
            hours, minutes, seconds = match.groups()
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except Exception:
        pass
    return 0.0


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int, max_lines: int = 3) -> list[str]:
    words = str(text or "").split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = current + " " + word
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while draw.textbbox((0, 0), lines[-1] + "…", font=font)[2] > max_width and len(lines[-1]) > 4:
            lines[-1] = lines[-1][:-1]
        if not lines[-1].endswith("…"):
            lines[-1] = lines[-1].rstrip(" .,;:") + "…"
    return lines


def _draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], font: ImageFont.ImageFont,
                  fill: tuple[int, int, int], max_width: int, line_gap: int = 8, max_lines: int = 3) -> int:
    x, y = xy
    lines = _wrap(draw, text, font, max_width, max_lines)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill, stroke_width=0)
        box = draw.textbbox((x, y), line, font=font)
        y += max(1, box[3] - box[1]) + line_gap
    return y


@lru_cache(maxsize=12)
def _gradient_overlay(size: tuple[int, int], rgba_top: tuple[int, int, int, int], rgba_bottom: tuple[int, int, int, int]) -> Image.Image:
    w, h = size
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    t = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    for c in range(4):
        arr[:, :, c] = np.broadcast_to((rgba_top[c] * (1.0 - t) + rgba_bottom[c] * t).astype(np.uint8), (h, w))
    return Image.fromarray(arr, mode="RGBA")


def _scene_frame(image: Image.Image, scene: dict[str, Any], details: dict[str, Any], frame_index: int,
                 frames_per_scene: int, size: tuple[int, int], palette: dict[str, tuple[int, int, int]]) -> np.ndarray:
    w, h = size
    # Soft Ken Burns push-in; the crop movement is deliberately restrained.
    progress = frame_index / max(1, frames_per_scene - 1)
    zoom = 1.025 + 0.07 * progress
    target = (max(w, int(w * zoom)), max(h, int(h * zoom)))
    bg = ImageOps.fit(image, target, method=Image.Resampling.LANCZOS, centering=(0.48 + 0.025 * progress, 0.47))
    left = max(0, (bg.width - w) // 2)
    top = max(0, (bg.height - h) // 2)
    bg = bg.crop((left, top, left + w, top + h)).convert("RGBA")

    # Cinematic scrims keep text legible without covering the entire property image.
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    top_grad = _gradient_overlay((w, h), (5, 9, 11, 168), (5, 9, 11, 0))
    bottom_grad = _gradient_overlay((w, h), (5, 9, 11, 0), (5, 9, 11, 224))
    overlay = Image.alpha_composite(overlay, top_grad)
    overlay = Image.alpha_composite(overlay, bottom_grad)
    bg = Image.alpha_composite(bg, overlay)
    d = ImageDraw.Draw(bg)

    vertical = h > w
    margin = int(w * (0.075 if vertical else 0.065))
    accent = palette["accent"]
    cream = palette["cream"]
    brand = str(scene.get("eyebrow") or "PROPERTY FILM").upper()

    # Top editorial masthead.
    d.rounded_rectangle((margin, int(h * 0.055), margin + int(w * 0.105), int(h * 0.055) + 5), radius=3, fill=accent)
    d.text((margin, int(h * 0.075)), brand[:34], font=_font(max(14, int(w * (0.018 if not vertical else 0.026))), bold=True), fill=cream, spacing=4)
    page_label = str(scene.get("tag") or "PROPERTY FILM").upper()
    page_font = _font(max(12, int(w * 0.014)), bold=True)
    pb = d.textbbox((0, 0), page_label, font=page_font)
    d.text((w - margin - (pb[2] - pb[0]), int(h * 0.078)), page_label, font=page_font, fill=(cream[0], cream[1], cream[2], 220))

    # Title lock-up sits low for portrait films and in the lower-left third for landscape.
    title_y = int(h * (0.59 if vertical else 0.52))
    if scene.get("kind") == "outro":
        title_y = int(h * (0.61 if vertical else 0.56))
    elif scene.get("kind") == "cover":
        title_y = int(h * (0.55 if vertical else 0.50))
    d.rounded_rectangle((margin, title_y - int(h * 0.035), margin + int(w * 0.075), title_y - int(h * 0.035) + 4), radius=2, fill=accent)

    if vertical:
        title_size = int(w * (0.085 if len(str(scene.get("headline", ""))) < 22 else 0.072))
        sub_size = int(w * 0.033)
        label_size = int(w * 0.021)
        max_title_width = w - 2 * margin
        title_bottom = _draw_wrapped(d, scene.get("headline", ""), (margin, title_y), _font(title_size, bold=True), cream,
                                     max_title_width, line_gap=max(6, int(w * 0.012)), max_lines=3)
        sub_y = title_bottom + int(h * 0.023)
        if scene.get("subline"):
            _draw_wrapped(d, scene["subline"], (margin, sub_y), _font(sub_size), cream, max_title_width, line_gap=5, max_lines=2)
        if scene.get("kind") == "feature":
            d.rounded_rectangle((margin, int(h * 0.90), margin + int(w * 0.23), int(h * 0.90) + 5), radius=3, fill=accent)
            d.text((margin, int(h * 0.915)), f"{details.get('property_name') or 'PROPERTY'}  /  {scene.get('eyebrow', '')}", font=_font(label_size, bold=True), fill=(cream[0], cream[1], cream[2], 225))
        else:
            price = str(details.get("price") or "").strip()
            if price and scene.get("kind") == "cover":
                badge_y = min(int(h * 0.86), max(title_bottom + int(h * 0.105), int(h * 0.79)))
                badge_font = _font(int(w * 0.039), bold=True)
                tx = margin + int(w * 0.032)
                ty = badge_y + int(w * 0.023)
                tb = d.textbbox((tx, ty), price, font=badge_font)
                d.rounded_rectangle((margin, badge_y, min(w-margin, tb[2]+int(w*0.07)), badge_y+int(w*0.105)), radius=8,
                                    fill=(9, 15, 16, 182), outline=(accent[0], accent[1], accent[2], 220), width=2)
                d.text((tx, ty), price, font=badge_font, fill=cream)
    else:
        title_size = int(h * (0.087 if len(str(scene.get("headline", ""))) < 24 else 0.068))
        sub_size = int(h * 0.036)
        max_title_width = int(w * 0.69)
        title_bottom = _draw_wrapped(d, scene.get("headline", ""), (margin, title_y), _font(title_size, bold=True), cream,
                                     max_title_width, line_gap=8, max_lines=3)
        if scene.get("subline"):
            _draw_wrapped(d, scene["subline"], (margin, title_bottom + int(h * 0.025)), _font(sub_size), cream,
                          max_title_width, line_gap=5, max_lines=2)
        price = str(details.get("price") or "").strip()
        if price and scene.get("kind") == "cover":
            badge_font = _font(int(h * 0.045), bold=True)
            by = int(h * 0.82)
            d.rounded_rectangle((margin, by, margin + int(w * 0.22), by + int(h * 0.085)), radius=8,
                                fill=(9, 15, 16, 178), outline=(accent[0], accent[1], accent[2], 220), width=2)
            d.text((margin + 18, by + 12), price, font=badge_font, fill=cream)

    # Footer progress motif and disclaimer-light brand mark.
    footer_y = h - int(h * 0.045)
    footer_label = f"{details.get('property_name') or 'PROPERTY'}  /  {scene.get('tag') or 'FILM'}"
    d.text((margin, footer_y), footer_label[:52].upper(), font=_font(max(10, int(w * 0.013)), bold=True), fill=(cream[0], cream[1], cream[2], 185))
    line_y = h - int(h * 0.018)
    d.rounded_rectangle((margin, line_y, w - margin, line_y + 3), radius=2, fill=(255, 255, 255, 65))
    idx = int(scene.get("index", 0))
    d.rounded_rectangle((margin, line_y, margin + max(20, int((w - 2*margin) * ((idx + 1) / max(1, int(scene.get("total", 1)))))), line_y + 3), radius=2, fill=accent)
    return np.asarray(bg.convert("RGB"), dtype=np.uint8)


def render_video(images: list[Image.Image], details: dict[str, Any], output_path: str | Path,
                 aspect_ratio: str = "9:16 · Reels / Shorts", scene_seconds: float = 2.8,
                 transition_seconds: float = 0.4, music_path: str | None = None,
                 voiceover_path: str | None = None, progress_callback: Callable[[float], None] | None = None,
                 output_scale: float = 1.0) -> dict[str, Any]:
    """Render MP4. Images are PIL objects. Requires 4-8 photos for assignment compliance."""
    if not 4 <= len(images) <= 8:
        raise ValueError(f"Add 4–8 property images before exporting. Received {len(images)}.")
    if scene_seconds < 1.5 or scene_seconds > 8:
        raise ValueError("Scene duration must be between 1.5 and 8 seconds.")

    ratio = aspect_ratio.split(" ")[0]
    if ratio == "16:9":
        size = (1280, 720)
    elif ratio == "1:1":
        size = (1080, 1080)
    elif ratio == "4:5":
        size = (864, 1080)
    else:
        size = (720, 1280)
    if not 0.4 <= float(output_scale) <= 1.0:
        raise ValueError("Output scale must be between 0.4 and 1.0.")
    if output_scale != 1.0:
        size = (max(2, int(size[0] * output_scale) // 2 * 2), max(2, int(size[1] * output_scale) // 2 * 2))
    w, h = size
    palette_key = str(details.get("tone") or "Architectural editorial")
    palette = PALETTES.get(palette_key, PALETTES["Architectural editorial"])
    scenes = build_scene_plan(details, len(images))
    for index, scene in enumerate(scenes):
        scene["index"] = index
        scene["total"] = len(scenes)

    frames_per_scene = max(36, int(round(scene_seconds * FPS)))
    transition_frames = min(max(1, int(round(transition_seconds * FPS))), max(1, frames_per_scene // 4))
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    has_voice = bool(voiceover_path and Path(voiceover_path).exists())
    has_music = bool(music_path and Path(music_path).exists())
    frames_total = len(scenes) * frames_per_scene - (len(scenes) - 1) * transition_frames
    video_seconds = frames_total / FPS
    # If the narration is longer than the slideshow, hold the last frame so it is not cut off.
    pad_seconds = 0.0
    if has_voice:
        pad_seconds = max(0.0, _audio_duration(ffmpeg, str(voiceover_path)) + 0.6 - video_seconds)

    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "pipe:0"]
    if has_voice:
        command += ["-i", str(voiceover_path)]
    if has_music:
        command += ["-stream_loop", "-1", "-i", str(music_path)]
    total_seconds = video_seconds + pad_seconds
    if pad_seconds > 0:
        command += ["-vf", f"tpad=stop_mode=clone:stop_duration={pad_seconds:.3f}"]
    if has_voice and has_music:
        command += ["-filter_complex", "[1:a]volume=1.0[voice];[2:a]volume=0.16[music];[voice][music]amix=inputs=2:duration=longest:dropout_transition=2:normalize=0[aout]",
                    "-map", "0:v:0", "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-t", f"{total_seconds:.3f}"]
    elif has_voice or has_music:
        audio_gain = "0.78" if has_voice else "0.18"
        command += ["-map", "0:v:0", "-map", "1:a:0", "-af", f"volume={audio_gain},apad", "-c:a", "aac", "-b:a", "160k", "-t", f"{total_seconds:.3f}"]
    else:
        command += ["-map", "0:v:0", "-an"]
    command += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output_path)]

    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    written_frames = 0
    planned_frames = frames_total
    previous_tail: list[np.ndarray] = []

    def emit(frame: np.ndarray) -> None:
        nonlocal written_frames
        proc.stdin.write(frame.tobytes())
        written_frames += 1
        if progress_callback and written_frames % 12 == 0:
            progress_callback(min(0.94, 0.02 + 0.9 * written_frames / max(1, planned_frames)))

    def make_frame(scene: dict[str, Any], image: Image.Image, frame_i: int) -> np.ndarray:
        return _scene_frame(image, scene, details, frame_i, frames_per_scene, size, palette)

    try:
        for scene_index, scene in enumerate(scenes):
            image = images[int(scene["image_index"])].convert("RGB")
            if scene_index == 0:
                # Stream the first scene except its final transition window.
                for frame_i in range(frames_per_scene - transition_frames):
                    emit(make_frame(scene, image, frame_i))
                previous_tail = [make_frame(scene, image, frame_i) for frame_i in range(frames_per_scene - transition_frames, frames_per_scene)]
            else:
                # Fade from the previous scene's held tail into this scene's first frames.
                head = [make_frame(scene, image, frame_i) for frame_i in range(transition_frames)]
                if len(previous_tail) != transition_frames:
                    raise RuntimeError("Could not construct the scene transition.")
                for i, (old, new_frame) in enumerate(zip(previous_tail, head)):
                    alpha = (i + 1) / (transition_frames + 1)
                    blended = np.clip(old.astype(np.float32) * (1.0 - alpha) + new_frame.astype(np.float32) * alpha, 0, 255).astype(np.uint8)
                    emit(blended)
                # Stream the body in sequence, then hold the tail for the next transition.
                middle_end = frames_per_scene - transition_frames
                for frame_i in range(transition_frames, middle_end):
                    emit(make_frame(scene, image, frame_i))
                previous_tail = [make_frame(scene, image, frame_i) for frame_i in range(middle_end, frames_per_scene)]
            if progress_callback:
                progress_callback(min(0.94, 0.03 + 0.89 * (scene_index + 1) / len(scenes)))

        # The final scene's tail is output as normal frames, not a transition source.
        for frame in previous_tail:
            emit(frame)
        proc.stdin.close()
        stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
        return_code = proc.wait()
        if return_code != 0:
            raise RuntimeError(f"FFmpeg could not export the MP4. {stderr[-1800:]}")
    except Exception:
        try:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
        except Exception:
            pass
        proc.kill()
        proc.wait()
        if output_path.exists():
            output_path.unlink(missing_ok=True)
        raise

    if progress_callback:
        progress_callback(1.0)
    script = generate_script(details)
    return {
        "path": str(output_path),
        "duration_seconds": round(written_frames / FPS + pad_seconds, 2),
        "frames": written_frames,
        "resolution": f"{w}x{h}",
        "scene_count": len(scenes),
        "voiceover_text": script["voiceover"],
        "file_size_mb": round(output_path.stat().st_size / (1024 * 1024), 2),
    }
