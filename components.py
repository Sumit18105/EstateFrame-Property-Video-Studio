"""Reusable visual components for the EstateFrame Streamlit workflow."""
from __future__ import annotations

import base64
import html
from io import BytesIO
from typing import Sequence

import streamlit as st
from PIL import Image


def image_data_uri(image: Image.Image, max_width: int = 1100) -> str:
    """Return a compact JPEG data URI for use in an inline cover preview."""
    resized = image.copy()
    if resized.width > max_width:
        new_height = max(1, int(resized.height * max_width / resized.width))
        resized = resized.resize((max_width, new_height), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    resized.save(buffer, format="JPEG", quality=82, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return "data:image/jpeg;base64," + encoded


def poster_html(image: Image.Image, details: dict) -> str:
    """Build a cover-card preview that reflects the current property details."""
    ratio = str(details.get("aspect_ratio", "16:9")).split(" ")[0]
    ratio_css = {"16:9": "16 / 9", "9:16": "9 / 16", "1:1": "1 / 1", "4:5": "4 / 5"}.get(ratio, "16 / 9")
    title = html.escape(str(details.get("property_name") or "Property showcase"))
    meta = " · ".join(
        value for value in (str(details.get("property_type") or ""), str(details.get("location") or "")) if value
    )
    price = html.escape(str(details.get("price") or "").strip())
    brand = html.escape(str(details.get("brand_name") or "EstateFrame").upper())
    image_url = image_data_uri(image)
    price_badge = f'<div class="poster-price">{price}</div>' if price else ""
    return f"""
    <div class="poster-frame" style="aspect-ratio:{ratio_css};background-image:url('{image_url}')">
      <div class="poster-overlay">
        <div class="poster-brand">{brand}</div>
        <div>
          <div style="height:3px;width:32px;background:#8B2D3A;border-radius:3px;margin-bottom:12px"></div>
          <div class="poster-title">{title}</div>
          <div class="poster-sub">{html.escape(meta)}</div>
          {price_badge}
        </div>
        <div class="poster-footer">PROPERTY VIDEO · {html.escape(ratio)}</div>
      </div>
    </div>
    """


def render_stepper(active_step: int, labels: Sequence[str] | None = None) -> None:
    """Render the Details → Photos → Style → Generate progress stepper."""
    labels = list(labels or ["Details", "Photos", "Style", "Generate"])
    parts: list[str] = ['<div class="stepper">']
    for index, label in enumerate(labels):
        state = "done" if index < active_step else ("active" if index == active_step else "")
        marker = "✓" if index < active_step else str(index + 1)
        parts.append(
            f'<div class="step-item {state}"><div class="step-node">{marker}</div><div class="step-name">{html.escape(label)}</div></div>'
        )
        if index < len(labels) - 1:
            line_state = "done" if index < active_step else ""
            parts.append(f'<div class="step-line {line_state}"></div>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)
