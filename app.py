from __future__ import annotations

import hashlib
import html
import json
import tempfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image, ImageOps

from components import poster_html as _poster_html, render_stepper as _render_stepper
from script_engine import generate_script, parse_features
from styles import apply_styles
from video_engine import render_video

ROOT = Path(__file__).resolve().parent
DEMO_DIR = ROOT / "assets" / "demo"
OUTPUT_DIR = ROOT / "outputs"
SAMPLE_VIDEO = ROOT / "sample_output" / "The_Meridian_Residences_demo.mp4"
SAMPLE_COVER = ROOT / "sample_output" / "cover_frame.jpg"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DATA = json.loads((ROOT / "sample_property.json").read_text(encoding="utf-8"))

st.set_page_config(
    page_title="EstateFrame | Property Film Studio",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_styles()

NAV_ITEMS = ["Home", "Create Video", "My Videos", "Templates"]
STYLE_MAP = {
    "Modern": "Architectural editorial",
    "Luxury": "Warm & welcoming",
    "Minimal": "Clean minimal",
    "Vibrant": "High contrast",
}
STYLE_COPY = {
    "Modern": "Clean typography and smooth transitions.",
    "Luxury": "Warm tones and a more editorial presentation.",
    "Minimal": "Restrained captions with a clean visual palette.",
    "Vibrant": "High-contrast title cards and stronger accents.",
}
FORMAT_OPTIONS = ["16:9 · Landscape", "9:16 · Portrait", "1:1 · Square"]
FEATURE_OPTIONS = [
    "Parking", "Balcony", "Gated Society", "Swimming Pool", "Garden",
    "Gym", "Lift", "Power Backup", "Furnished", "Security", "Modular Kitchen",
    "Clubhouse", "Terrace", "Park Facing", "Visitor Parking",
]
STEP_LABELS = ["Details", "Photos", "Style", "Generate"]


def _demo_photo_items() -> list[dict[str, Any]]:
    captions = list(SAMPLE_DATA.get("photo_captions", SAMPLE_DATA.get("key_features", [])))
    items: list[dict[str, Any]] = []
    for idx, path in enumerate(sorted(DEMO_DIR.glob("*.jpg"))[:8]):
        caption = captions[idx] if idx < len(captions) else f"Property detail {idx + 1}"
        items.append({"name": path.name, "data": path.read_bytes(), "caption": caption})
    return items


def _reset_sample_project() -> None:
    st.session_state["property_name"] = SAMPLE_DATA.get("property_name", "The Meridian Residences")
    st.session_state["location"] = SAMPLE_DATA.get("location", "")
    st.session_state["property_type"] = SAMPLE_DATA.get("property_type", "Apartment")
    st.session_state["price"] = SAMPLE_DATA.get("price", "")
    st.session_state["bedrooms"] = int(SAMPLE_DATA.get("bedrooms", 3))
    st.session_state["bathrooms"] = int(SAMPLE_DATA.get("bathrooms", 2))
    st.session_state["area_sqft"] = int(SAMPLE_DATA.get("area_sqft", 1200))
    st.session_state["short_description"] = SAMPLE_DATA.get(
        "short_description", "A modern home with a comfortable layout and thoughtfully planned interiors."
    )
    st.session_state["selected_features"] = list(SAMPLE_DATA.get("key_features", []))
    st.session_state["custom_features"] = ""
    st.session_state["cta"] = st.session_state.get("default_cta") or SAMPLE_DATA.get("cta", "Enquire today")
    st.session_state["brand_name"] = st.session_state.get("default_brand_name") or SAMPLE_DATA.get("brand_name", "ESTATEFRAME FILMS")
    st.session_state["visual_style"] = "Modern"
    st.session_state["video_format"] = "16:9 · Landscape"
    st.session_state["scene_seconds"] = 3.7
    st.session_state["voice_mode"] = "No narration"
    st.session_state["photo_items"] = _demo_photo_items()
    st.session_state["photo_source"] = "demo"
    st.session_state["photo_widget_version"] = int(st.session_state.get("photo_widget_version", 0)) + 1
    st.session_state["last_upload_signature"] = ""
    st.session_state["music_bytes"] = b""
    st.session_state["music_name"] = ""
    st.session_state["music_widget_version"] = int(st.session_state.get("music_widget_version", 0)) + 1
    st.session_state["last_output_path"] = ""
    st.session_state["last_output_meta"] = None
    st.session_state["last_output_details"] = None
    st.session_state["generation_error"] = ""
    st.session_state["pending_generate"] = False
    st.session_state["current_step"] = 0
    st.session_state["script_details_signature"] = ""
    st.session_state["show_sample_video"] = False
    st.session_state["route_override"] = "Create Video"


def _init_state() -> None:
    defaults: dict[str, Any] = {
        "navigation": "Home",
        "route_override": "",
        "current_step": 0,
        "property_name": SAMPLE_DATA.get("property_name", "The Meridian Residences"),
        "location": SAMPLE_DATA.get("location", "Sector 82, Mohali"),
        "property_type": SAMPLE_DATA.get("property_type", "Apartment"),
        "price": SAMPLE_DATA.get("price", "₹1.25 Cr"),
        "bedrooms": int(SAMPLE_DATA.get("bedrooms", 3)),
        "bathrooms": int(SAMPLE_DATA.get("bathrooms", 2)),
        "area_sqft": int(SAMPLE_DATA.get("area_sqft", 1200)),
        "short_description": SAMPLE_DATA.get(
            "short_description", "A modern home with a comfortable layout and thoughtfully planned interiors."
        ),
        "selected_features": list(SAMPLE_DATA.get("key_features", [])),
        "custom_features": "",
        "cta": SAMPLE_DATA.get("cta", "Book a site visit"),
        "brand_name": SAMPLE_DATA.get("brand_name", "MERIDIAN / PROPERTY FILMS"),
        "visual_style": "Modern",
        "video_format": "16:9 · Landscape",
        "scene_seconds": 3.7,
        "voice_mode": "No narration",
        "music_bytes": b"",
        "music_name": "",
        "music_widget_version": 0,
        "photo_items": _demo_photo_items(),
        "photo_source": "demo",
        "photo_widget_version": 0,
        "last_upload_signature": "",
        "last_output_path": "",
        "last_output_meta": None,
        "last_output_details": None,
        "history": [],
        "pending_generate": False,
        "generation_error": "",
        "show_sample_video": False,
        "default_brand_name": SAMPLE_DATA.get("brand_name", "ESTATEFRAME FILMS"),
        "default_cta": SAMPLE_DATA.get("cta", "Enquire today"),
        "script_details_signature": "",
        "voiceover_script": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Main-page actions are routed before the navigation widget is created.
    route = st.session_state.get("route_override")
    if route in NAV_ITEMS:
        st.session_state["navigation"] = route
        st.session_state["route_override"] = ""
    if st.session_state.get("navigation") not in NAV_ITEMS:
        st.session_state["navigation"] = "Home"


WIDGET_STATE_KEYS = [
    "property_name", "location", "property_type", "price", "cta", "bedrooms", "bathrooms",
    "area_sqft", "short_description", "selected_features", "custom_features", "brand_name",
    "visual_style", "video_format", "scene_seconds", "voice_mode", "voiceover_script",
]


def _persist_widget_state() -> None:
    """Streamlit deletes a widget's state when it is not rendered in a run (e.g. on another
    step). Re-assigning each key keeps the user's values instead of resetting to defaults."""
    for key in WIDGET_STATE_KEYS:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


def _current_features() -> list[str]:
    selected = st.session_state.get("selected_features", []) or []
    extra = parse_features(st.session_state.get("custom_features", ""))
    return parse_features(list(selected) + extra)


def _details() -> dict[str, Any]:
    return {
        "property_name": str(st.session_state.get("property_name", "")).strip(),
        "location": str(st.session_state.get("location", "")).strip(),
        "price": str(st.session_state.get("price", "")).strip(),
        "property_type": str(st.session_state.get("property_type", "Apartment")).strip(),
        "bedrooms": st.session_state.get("bedrooms", ""),
        "bathrooms": st.session_state.get("bathrooms", ""),
        "area_sqft": st.session_state.get("area_sqft", ""),
        "short_description": str(st.session_state.get("short_description", "")).strip(),
        "key_features": "\n".join(_current_features()),
        "scene_captions": "\n".join(str(item.get("caption", "")).strip() for item in st.session_state.get("photo_items", [])),
        "cta": str(st.session_state.get("cta", "")).strip(),
        "brand_name": str(st.session_state.get("brand_name", "")).strip(),
        "tone": STYLE_MAP.get(st.session_state.get("visual_style", "Modern"), "Architectural editorial"),
        "visual_style": st.session_state.get("visual_style", "Modern"),
        "aspect_ratio": st.session_state.get("video_format", "16:9 · Landscape"),
    }


def _script_signature(details: dict[str, Any]) -> str:
    keys = [
        "property_name", "location", "price", "property_type", "bedrooms",
        "bathrooms", "area_sqft", "short_description", "key_features", "cta",
    ]
    facts = {key: details.get(key, "") for key in keys}
    return hashlib.sha1(json.dumps(facts, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _ensure_script_draft(force: bool = False) -> None:
    details = _details()
    signature = _script_signature(details)
    if force or signature != st.session_state.get("script_details_signature"):
        st.session_state["voiceover_script"] = generate_script(details)["voiceover"]
        st.session_state["script_details_signature"] = signature


def _force_regenerate_script() -> None:
    _ensure_script_draft(force=True)


def _image_from_item(item: dict[str, Any]) -> Image.Image:
    with Image.open(BytesIO(item["data"])) as image:
        return ImageOps.exif_transpose(image).convert("RGB")


def _current_images() -> list[Image.Image]:
    images: list[Image.Image] = []
    for item in st.session_state.get("photo_items", [])[:8]:
        try:
            images.append(_image_from_item(item))
        except Exception:
            continue
    return images




def _go_to(page: str) -> None:
    st.session_state["route_override"] = page
    st.rerun()


def _move_photo(index: int, delta: int) -> None:
    items = st.session_state.get("photo_items", [])
    target = index + delta
    if 0 <= target < len(items):
        items[index], items[target] = items[target], items[index]
        st.session_state["photo_items"] = items
        st.session_state["photo_source"] = "user"
        st.session_state["photo_widget_version"] += 1
        st.session_state["last_upload_signature"] = ""


def _remove_photo(index: int) -> None:
    items = st.session_state.get("photo_items", [])
    if 0 <= index < len(items):
        items.pop(index)
        st.session_state["photo_items"] = items
        st.session_state["photo_source"] = "user"
        st.session_state["photo_widget_version"] += 1
        st.session_state["last_upload_signature"] = ""


def _apply_template(style: str) -> None:
    st.session_state["visual_style"] = style
    st.session_state["current_step"] = 2
    st.session_state["route_override"] = "Create Video"


def _save_preferences() -> None:
    st.session_state["default_brand_name"] = str(st.session_state.get("settings_brand_name", "")).strip()
    st.session_state["default_cta"] = str(st.session_state.get("settings_cta", "")).strip()
    st.session_state["preferences_saved"] = True


def _sync_uploads(uploaded_files: list[Any] | None) -> list[str]:
    warnings: list[str] = []
    if not uploaded_files:
        return warnings
    signature = "|".join(f"{file.name}:{getattr(file, 'size', 0)}" for file in uploaded_files)
    if signature == st.session_state.get("last_upload_signature"):
        return warnings

    incoming: list[dict[str, Any]] = []
    current_items = st.session_state.get("photo_items", [])
    old_captions = {str(item.get("name")): str(item.get("caption", "")) for item in current_items}
    existing_names = {str(item.get("name")) for item in current_items}
    for file in list(uploaded_files)[:8]:
        raw = file.getvalue()
        if len(raw) > 10 * 1024 * 1024:
            warnings.append(f"{file.name}: file exceeds the 10 MB limit and was skipped.")
            continue
        try:
            with Image.open(BytesIO(raw)) as image:
                image_format = (image.format or "").upper()
                if image_format not in {"JPEG", "PNG"}:
                    warnings.append(f"{file.name}: use a JPG, JPEG, or PNG image.")
                    continue
                image.verify()
        except Exception:
            warnings.append(f"{file.name}: this file could not be read as a valid image.")
            continue
        incoming.append({
            "name": file.name,
            "data": raw,
            "caption": old_captions.get(file.name, ""),
        })

    if len(uploaded_files) > 8:
        warnings.append("Only the first 8 selected files can be used.")

    if incoming:
        if st.session_state.get("photo_source") == "demo":
            next_items = incoming
        elif not st.session_state.get("last_upload_signature"):
            next_items = list(current_items)
            for item in incoming:
                if item["name"] not in existing_names:
                    next_items.append(item)
        else:
            # The uploader retains the active selection, so use that selection as the new set.
            next_items = incoming
        if len(next_items) > 8 and len(uploaded_files) <= 8:
            warnings.append("A project can contain at most 8 photos total; extra photos were skipped.")
        st.session_state["photo_items"] = next_items[:8]
        st.session_state["photo_source"] = "user"
        for idx, item in enumerate(st.session_state["photo_items"]):
            if not item.get("caption"):
                item["caption"] = f"Property scene {idx + 1:02d}"
        # Rotate the uploader key so the accepted selection clears and the user can add more later.
        st.session_state["last_upload_signature"] = ""
        st.session_state["photo_widget_version"] += 1
    else:
        # Clear an invalid file selection so the user can retry without refreshing the app.
        st.session_state["last_upload_signature"] = ""
        st.session_state["photo_widget_version"] += 1
    return warnings


def _top_nav() -> str:
    """Render the premium horizontal navigation without Streamlit's sidebar."""
    page = st.session_state.get("navigation", "Home")
    with st.container(key="top_navigation"):
        columns = st.columns([2.25, .85, 1.25, 1.05, .85], gap="small", vertical_alignment="center")
        with columns[0]:
            st.markdown(
                '<div class="brand-lockup"><div class="brand-mark">EF</div><div>'
                '<div class="brand-name">EstateFrame</div><div class="brand-sub">PROPERTY FILM STUDIO</div>'
                '</div></div>',
                unsafe_allow_html=True,
            )
        visible = ["Home", "Create Video", "My Videos", "Templates"]
        for idx, item in enumerate(visible, start=1):
            with columns[idx]:
                slug = item.lower().replace(" ", "_")
                state = "active" if item == page else "idle"
                if st.button(item, key=f"top_nav_{slug}_{state}", width="stretch"):
                    if item == "Create Video" and page != "Create Video":
                        st.session_state["current_step"] = 0
                        st.session_state["last_output_path"] = ""
                        st.session_state["last_output_meta"] = None
                        st.session_state["last_output_details"] = None
                        st.session_state["generation_error"] = ""
                        st.session_state["pending_generate"] = False
                    _go_to(item)
    return page

def _render_home() -> None:
    items = st.session_state.get("photo_items", [])
    image = _image_from_item(items[0]) if items else Image.open(SAMPLE_COVER).convert("RGB")

    left, right = st.columns([.92, 1.08], gap="large", vertical_alignment="center")
    with left:
        st.markdown('<div class="page-eyebrow">PROPERTY FILM STUDIO</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-title">Turn property photos<br>into <span>stunning videos</span></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-desc">Create a cinematic property film from verified listing details and 4–8 photos. Review the scenes, then export your MP4.</div>',
            unsafe_allow_html=True,
        )
        action_col, secondary_col = st.columns([1.12, .88], gap="small")
        with action_col:
            if st.button("Create New Video  →", type="primary", width="stretch", key="home_create_video"):
                st.session_state["current_step"] = 0
                _go_to("Create Video")
        with secondary_col:
            if st.button("View Examples", width="stretch", key="home_preview_sample"):
                st.session_state["show_sample_video"] = not st.session_state.get("show_sample_video", False)
                st.rerun()
    with right:
        with st.container(border=True):
            st.image(image, width="stretch")
            location = st.session_state.get("location", "") if st.session_state.get("photo_source") != "demo" else SAMPLE_DATA.get("location", "")
            name = st.session_state.get("property_name", "Property preview")
            st.markdown(
                f'<div class="hero-image-caption"><div><strong>{html.escape(str(name))}</strong><br>'
                f'<span>{html.escape(str(location))}</span></div><span class="hero-chip">SAMPLE PROJECT</span></div>',
                unsafe_allow_html=True,
            )

    if st.session_state.get("show_sample_video"):
        if SAMPLE_VIDEO.exists():
            with st.container(border=True):
                st.markdown('<div class="card-title">Sample property film</div>', unsafe_allow_html=True)
                st.video(str(SAMPLE_VIDEO))
        else:
            st.info("The bundled sample MP4 is not available in this project folder.")

    st.markdown('<div class="section-label">THE WORKFLOW</div>', unsafe_allow_html=True)
    workflow_cols = st.columns(4, gap="medium")
    features = [
        ("01", "Property details", "Add verified listing facts."),
        ("02", "Photo upload", "Choose and order 4–8 images."),
        ("03", "Script & style", "Review captions and format."),
        ("04", "Generate & export", "Preview and download MP4."),
    ]
    for col, (number, title, description) in zip(workflow_cols, features):
        with col:
            st.markdown(
                f'<div class="feature-card"><div class="feature-icon">{number}</div>'
                f'<div class="feature-title">{title}</div><div class="feature-desc">{description}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-head"><div><div class="section-label">EXAMPLES</div>'
                '<div class="card-title">Sample property scenes</div></div></div>', unsafe_allow_html=True)
    gallery = _demo_photo_items()[:4]
    gallery_cols = st.columns(4, gap="medium")
    gallery_labels = ["Exterior", "Living room", "Kitchen", "Primary suite"]
    for idx, (col, item) in enumerate(zip(gallery_cols, gallery)):
        with col:
            st.image(_image_from_item(item), width="stretch")
            st.markdown(
                f'<div class="sample-name">{gallery_labels[idx]}</div>'
                '<div class="sample-location">Sector 82, Mohali · Sample</div>',
                unsafe_allow_html=True,
            )

def _render_details_step() -> None:
    details = _details()
    form_col, preview_col = st.columns([1.18, .82], gap="large")
    with form_col:
        with st.container(border=True):
            st.markdown('<div class="card-title">Property details</div><div class="card-subtitle">Use verified information from the listing.</div>', unsafe_allow_html=True)
            if st.session_state.get("property_name") == SAMPLE_DATA.get("property_name") and st.session_state.get("photo_source") == "demo":
                st.markdown('<div class="muted-note">Sample listing loaded — replace details and photos before publishing.</div>', unsafe_allow_html=True)
            st.text_input("Property name *", key="property_name", placeholder="e.g. Skyline Residency")
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                st.text_input("Location *", key="location", placeholder="City or neighbourhood")
            with col2:
                st.selectbox(
                    "Property type",
                    ["Apartment", "Villa", "Independent house", "Plot", "Commercial", "Other"],
                    key="property_type",
                )
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                st.text_input("Price", key="price", placeholder="e.g. ₹1.25 Cr")
            with col2:
                st.text_input("Enquiry text", key="cta", placeholder="e.g. Book a site visit")
            col1, col2, col3 = st.columns(3, gap="small")
            with col1:
                st.selectbox("Bedrooms", [1, 2, 3, 4, 5, 6], key="bedrooms")
            with col2:
                st.selectbox("Bathrooms", [1, 2, 3, 4, 5, 6], key="bathrooms")
            with col3:
                st.number_input("Area (sq ft)", min_value=0, max_value=100000, step=50, key="area_sqft")
            st.text_area("Short description", key="short_description", height=88, placeholder="A concise description using supplied property facts.")
            current_features = _current_features()
            feature_options = list(dict.fromkeys(FEATURE_OPTIONS + current_features))
            st.multiselect("Key features", feature_options, key="selected_features", placeholder="Select features from the listing")
            st.text_input("Add custom features", key="custom_features", placeholder="Separate multiple features with commas")
            with st.expander("Branding", expanded=False):
                st.text_input("Brand / agency name", key="brand_name", placeholder="Optional")
    with preview_col:
        with st.container(border=True):
            st.markdown('<div class="card-title">Live cover preview</div><div class="card-subtitle">Updates as you edit the listing.</div>', unsafe_allow_html=True)
            preview_images = _current_images()
            cover = preview_images[0] if preview_images else Image.open(SAMPLE_COVER).convert("RGB")
            st.markdown(_poster_html(cover, _details()), unsafe_allow_html=True)
            st.markdown("<div style='height:.55rem'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3, gap="small")
            with col1:
                st.metric("Photos", len(st.session_state.get("photo_items", [])))
            with col2:
                st.metric("Format", str(st.session_state.get("video_format", "16:9")).split(" ")[0])
            with col3:
                st.metric("Style", st.session_state.get("visual_style", "Modern"))
            st.markdown('<div class="muted-note">The video uses only your entered listing details and selected photos.</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)
    back_col, next_col = st.columns([1, 1], gap="medium")
    with back_col:
        if st.button("←  Home", key="details_back"):
            _go_to("Home")
    with next_col:
        if st.button("Next: Upload Photos  →", type="primary", width="stretch", key="details_next"):
            missing = []
            if not st.session_state.get("property_name", "").strip():
                missing.append("property name")
            if not st.session_state.get("location", "").strip():
                missing.append("location")
            if missing:
                st.error("Please enter the required " + " and ".join(missing) + ".")
            else:
                st.session_state["current_step"] = 1
                st.rerun()


def _render_photos_step() -> None:
    st.markdown('<div class="card-title">Upload property photos</div><div class="card-subtitle">Add 4–8 clear JPG, JPEG or PNG images. Reorder scenes to control the video sequence.</div>', unsafe_allow_html=True)
    upload_key = f"photo_upload_{st.session_state['photo_widget_version']}"
    uploaded = st.file_uploader(
        "Drag and drop property photos here, or browse files",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=upload_key,
        help="JPG, JPEG, PNG · Up to 8 photos · 10 MB each",
    )
    warnings = _sync_uploads(uploaded)
    for warning in warnings:
        st.warning(warning)

    items = st.session_state.get("photo_items", [])
    count = len(items)
    source_text = "Sample photos · AI-generated" if st.session_state.get("photo_source") == "demo" else "Uploaded photos"
    count_color = "#A9D9B7" if 4 <= count <= 8 else "#E5B2B8"
    count_bg = "#243B2C" if 4 <= count <= 8 else "#4A242A"
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin:.45rem 0 .8rem"><div class="card-title">{source_text} ({count}/8)</div><span class="pill" style="color:{count_color};background:{count_bg}">{"Ready to continue" if 4 <= count <= 8 else "Need 4–8 photos"}</span></div>',
        unsafe_allow_html=True,
    )

    if items:
        grid_cols = 3
        for start in range(0, len(items), grid_cols):
            cols = st.columns(grid_cols, gap="medium")
            for offset, col in enumerate(cols):
                index = start + offset
                if index >= len(items):
                    continue
                item = items[index]
                with col:
                    with st.container(border=True):
                        try:
                            st.image(_image_from_item(item), width="stretch")
                        except Exception:
                            st.error("Image unavailable")
                        st.markdown(f'<div class="photo-label">{index + 1:02d} · {html.escape(item["name"])}</div>', unsafe_allow_html=True)
                        caption_key = f"photo_caption_{st.session_state['photo_widget_version']}_{index}"
                        caption_value = st.text_input(
                            "Scene caption",
                            value=str(item.get("caption", "")),
                            key=caption_key,
                            label_visibility="visible",
                            placeholder="e.g. Bright living room",
                        )
                        st.session_state["photo_items"][index]["caption"] = caption_value
                        action_cols = st.columns([.7, .7, 1.1], gap="small")
                        with action_cols[0]:
                            st.button("↑", key=f"photo_up_{st.session_state['photo_widget_version']}_{index}", help="Move photo earlier", disabled=index == 0, on_click=_move_photo, args=(index, -1), width="stretch")
                        with action_cols[1]:
                            st.button("↓", key=f"photo_down_{st.session_state['photo_widget_version']}_{index}", help="Move photo later", disabled=index == len(items) - 1, on_click=_move_photo, args=(index, 1), width="stretch")
                        with action_cols[2]:
                            st.button("Remove", key=f"photo_remove_{st.session_state['photo_widget_version']}_{index}", on_click=_remove_photo, args=(index,), width="stretch")
    else:
        st.info("Upload 4–8 property photos to build the scene sequence.")

    if not 4 <= count <= 8:
        st.warning("The video export requires 4–8 valid photos.")

    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    back_col, next_col = st.columns([1, 1], gap="medium")
    with back_col:
        if st.button("←  Back to Details", key="photos_back"):
            st.session_state["current_step"] = 0
            st.rerun()
    with next_col:
        if st.button("Next: Video Style  →", type="primary", width="stretch", key="photos_next", disabled=not (4 <= count <= 8)):
            st.session_state["current_step"] = 2
            st.rerun()


def _render_style_step() -> None:
    st.markdown("<div class='card-title'>Video style</div><div class='card-subtitle'>Choose a visual treatment and export format. You can edit the script before generating.</div>", unsafe_allow_html=True)
    style_cols = st.columns(4, gap="medium")
    demo_items = _demo_photo_items()
    for idx, (col, style) in enumerate(zip(style_cols, STYLE_COPY.keys())):
        with col:
            with st.container(border=True):
                if demo_items:
                    st.image(_image_from_item(demo_items[min(idx, len(demo_items) - 1)]), width="stretch")
                selected = st.session_state.get("visual_style") == style
                st.markdown(f'<div class="style-title">{html.escape(style)} {"✓" if selected else ""}</div><div class="style-desc">{html.escape(STYLE_COPY[style])}</div>', unsafe_allow_html=True)
                if st.button("Selected" if selected else "Select style", key=f"select_style_{style}", type="primary" if selected else "secondary", width="stretch"):
                    st.session_state["visual_style"] = style
                    st.rerun()

    settings_col, audio_col = st.columns([1, 1], gap="large")
    with settings_col:
        with st.container(border=True):
            st.markdown('<div class="card-title">Video format and timing</div>', unsafe_allow_html=True)
            st.radio("Video format", FORMAT_OPTIONS, key="video_format", horizontal=True)
            st.slider("Scene duration", min_value=2.5, max_value=5.0, step=0.1, key="scene_seconds", help="Longer scenes create a slower-paced video.")
            total_scenes = len(st.session_state.get("photo_items", [])) + 2
            approx_duration = max(0, total_scenes * float(st.session_state.get("scene_seconds", 3.7)) - (total_scenes - 1) * .4)
            st.caption(f"Estimated video duration: about {approx_duration:.0f} seconds")
    with audio_col:
        with st.container(border=True):
            st.markdown('<div class="card-title">Audio</div><div class="card-subtitle">Narration uses an online text-to-speech service. Music is optional.</div>', unsafe_allow_html=True)
            st.radio("Voice-over", ["No narration", "English narration (online)"], key="voice_mode", horizontal=False)
            audio = st.file_uploader(
                "Background music (optional)",
                type=["mp3", "wav", "m4a", "aac", "ogg"],
                key=f"background_music_upload_{st.session_state['music_widget_version']}",
                help="Use audio you have permission to publish.",
            )
            if audio is not None:
                st.session_state["music_bytes"] = audio.getvalue()
                st.session_state["music_name"] = audio.name
            if st.session_state.get("music_name"):
                st.markdown(f'<span class="pill">Audio attached · {html.escape(st.session_state["music_name"])}</span>', unsafe_allow_html=True)
                if st.button("Remove background music", key="remove_background_music"):
                    st.session_state["music_bytes"] = b""
                    st.session_state["music_name"] = ""
                    st.session_state["music_widget_version"] += 1
                    st.rerun()

    with st.container(border=True):
        st.markdown('<div class="card-title">Narration script</div><div class="card-subtitle">Template-generated from the listing facts. Edit it before export if needed.</div>', unsafe_allow_html=True)
        st.text_area("Script", key="voiceover_script", height=125, label_visibility="collapsed")
        st.button("↻  Regenerate script from details", key="regenerate_script", on_click=_force_regenerate_script)

    st.markdown("<div style='height:.35rem'></div>", unsafe_allow_html=True)
    back_col, generate_col = st.columns([1, 1], gap="medium")
    with back_col:
        if st.button("←  Back to Photos", key="style_back"):
            st.session_state["current_step"] = 1
            st.rerun()
    with generate_col:
        if st.button("Generate Video  →", type="primary", width="stretch", key="style_generate"):
            missing = []
            if not st.session_state.get("property_name", "").strip():
                missing.append("property name")
            if not st.session_state.get("location", "").strip():
                missing.append("location")
            count = len(st.session_state.get("photo_items", []))
            if not 4 <= count <= 8:
                st.error("Add 4–8 usable photos before generating the video.")
            elif missing:
                st.error("Enter the required " + " and ".join(missing) + " before generating.")
            else:
                st.session_state["generation_error"] = ""
                st.session_state["last_output_path"] = ""
                st.session_state["last_output_meta"] = None
                st.session_state["last_output_details"] = None
                st.session_state["pending_generate"] = True
                st.session_state["current_step"] = 3
                st.rerun()


def _execute_generation() -> None:
    st.session_state["pending_generate"] = False
    details = _details()
    images = _current_images()
    if not 4 <= len(images) <= 8:
        st.session_state["generation_error"] = "Add 4–8 valid photos before exporting."
        return

    status_box = st.empty()
    progress_bar = st.progress(0, text="Preparing property photos…")
    stage_area = st.empty()
    st.markdown('<div class="muted-note">Generation runs locally. The export button appears after the MP4 has been written successfully.</div>', unsafe_allow_html=True)
    stage_area.markdown(
        '<div class="status-row"><span class="status-icon complete">✓</span>Preparing property photos</div>'
        '<div class="status-row"><span class="status-icon complete">✓</span>Preparing captions and script</div>'
        '<div class="status-row"><span class="status-icon">◌</span>Rendering scenes and encoding MP4</div>',
        unsafe_allow_html=True,
    )

    voice_path: str | None = None
    music_path: str | None = None
    output_path: Path | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="estateframe_") as temp_dir:
            temp_path = Path(temp_dir)
            if st.session_state.get("music_bytes"):
                music_path = str(temp_path / (Path(st.session_state.get("music_name") or "background.mp3").name))
                Path(music_path).write_bytes(st.session_state["music_bytes"])
            if st.session_state.get("voice_mode") == "English narration (online)":
                try:
                    from gtts import gTTS
                    voice_path = str(temp_path / "narration.mp3")
                    narration = str(st.session_state.get("voiceover_script", "")).strip()
                    if narration:
                        gTTS(text=narration, lang="en", tld="co.in", slow=False).save(voice_path)
                    else:
                        voice_path = None
                except Exception:
                    voice_path = None
                    status_box.warning("Online narration was unavailable. The video will export without narration.")

            slug = "".join(char.lower() if char.isalnum() else "_" for char in (details["property_name"] or "property_video")).strip("_")[:48]
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = OUTPUT_DIR / f"{slug or 'property_video'}_{stamp}.mp4"
            last_percent = [-1]

            def update_progress(fraction: float) -> None:
                percent = max(0, min(100, int(fraction * 100)))
                if percent == last_percent[0]:
                    return
                last_percent[0] = percent
                label = "Rendering scenes and encoding MP4…" if percent < 96 else "Finalizing MP4…"
                progress_bar.progress(percent, text=f"{label} {percent}%")
                stage_area.markdown(
                    '<div class="status-row"><span class="status-icon complete">✓</span>Preparing property photos</div>'
                    '<div class="status-row"><span class="status-icon complete">✓</span>Preparing captions and script</div>'
                    f'<div class="status-row"><span class="status-icon">◌</span>{html.escape(label)}</div>',
                    unsafe_allow_html=True,
                )

            result = render_video(
                images=images,
                details=details,
                output_path=output_path,
                aspect_ratio=details["aspect_ratio"],
                scene_seconds=float(st.session_state.get("scene_seconds", 3.7)),
                transition_seconds=0.4,
                music_path=music_path,
                voiceover_path=voice_path,
                progress_callback=update_progress,
            )
        result["voiceover_text"] = str(st.session_state.get("voiceover_script", ""))
        result["style"] = st.session_state.get("visual_style", "Modern")
        result["audio_status"] = "Narration + music" if voice_path and music_path else ("Narration" if voice_path else ("Background music" if music_path else "No audio"))
        st.session_state["last_output_path"] = str(output_path)
        st.session_state["last_output_meta"] = result
        st.session_state["last_output_details"] = details.copy()
        st.session_state["generation_error"] = ""
        st.session_state["history"].insert(0, {
            "path": str(output_path),
            "name": details.get("property_name") or "Property video",
            "location": details.get("location", ""),
            "created_at": datetime.now().strftime("%d %b %Y, %H:%M"),
            "meta": result.copy(),
            "details": details.copy(),
        })
        st.session_state["history"] = st.session_state["history"][:20]
        progress_bar.progress(100, text="MP4 ready")
        status_box.success("Video exported successfully.")
        stage_area.markdown(
            '<div class="status-row"><span class="status-icon complete">✓</span>Preparing property photos</div>'
            '<div class="status-row"><span class="status-icon complete">✓</span>Preparing captions and script</div>'
            '<div class="status-row"><span class="status-icon complete">✓</span>MP4 exported successfully</div>',
            unsafe_allow_html=True,
        )
    except Exception as exc:
        if output_path and output_path.exists():
            output_path.unlink(missing_ok=True)
        st.session_state["generation_error"] = str(exc).splitlines()[0][:260] or "Video export failed."
        status_box.empty()


def _render_result() -> None:
    path_str = st.session_state.get("last_output_path", "")
    if not path_str or not Path(path_str).exists():
        st.info("No exported video is available yet.")
        if st.button("Return to Video Style", key="result_back_style"):
            st.session_state["current_step"] = 2
            st.rerun()
        return
    path = Path(path_str)
    meta = st.session_state.get("last_output_meta") or {}
    details = st.session_state.get("last_output_details") or _details()
    st.markdown(
        '<div class="result-success"><div class="result-check">✓</div><div><div class="result-title">Your property video is ready</div><div class="result-sub">MP4 export completed successfully.</div></div></div>',
        unsafe_allow_html=True,
    )
    video_col, details_col = st.columns([1.55, .75], gap="large")
    with video_col:
        with st.container(border=True):
            st.video(str(path))
            st.download_button(
                "↓  Download MP4",
                data=path.read_bytes(),
                file_name=path.name,
                mime="video/mp4",
                type="primary",
                width="stretch",
                key=f"download_{path.name}",
            )
    with details_col:
        with st.container(border=True):
            st.markdown('<div class="card-title">Video details</div>', unsafe_allow_html=True)
            st.markdown(f"**Property**  \n{html.escape(str(details.get('property_name') or 'Property video'))}")
            st.markdown(f"**Location**  \n{html.escape(str(details.get('location') or '—'))}")
            st.markdown(f"**Duration**  \n{meta.get('duration_seconds', '—')} sec")
            st.markdown(f"**Resolution**  \n{html.escape(str(meta.get('resolution', '—')))}")
            st.markdown(f"**Style**  \n{html.escape(str(meta.get('style', details.get('visual_style', 'Modern'))))}")
            st.markdown(f"**Audio**  \n{html.escape(str(meta.get('audio_status', 'No audio')))}")
            st.markdown(f"**File size**  \n{meta.get('file_size_mb', '—')} MB")
    st.markdown("### Scene breakdown")
    items = st.session_state.get("photo_items", [])
    scene_cols = st.columns(min(max(1, len(items)), 6), gap="small")
    for idx, (col, item) in enumerate(zip(scene_cols, items[:6])):
        with col:
            st.image(_image_from_item(item), width="stretch")
            st.caption(f"{idx + 1:02d} · {item.get('caption') or 'Property scene'}")
    back_col, new_col = st.columns([1, 1], gap="medium")
    with back_col:
        if st.button("Edit Settings", key="result_edit_settings"):
            st.session_state["current_step"] = 2
            st.rerun()
    with new_col:
        if st.button("Generate Another", type="primary", width="stretch", key="result_new_video"):
            st.session_state["last_output_path"] = ""
            st.session_state["last_output_meta"] = None
            st.session_state["last_output_details"] = None
            st.session_state["generation_error"] = ""
            st.session_state["current_step"] = 0
            st.rerun()


def _render_generate_step() -> None:
    if st.session_state.get("pending_generate"):
        _execute_generation()

    error = st.session_state.get("generation_error", "")
    path = st.session_state.get("last_output_path", "")
    if error and (not path or not Path(path).exists()):
        st.error(f"Video generation failed: {error}")
        st.markdown('<div class="muted-note">Your property details and photos are preserved. Correct the issue or retry the export.</div>', unsafe_allow_html=True)
        retry_col, back_col = st.columns([1, 1], gap="medium")
        with retry_col:
            if st.button("Retry generation", type="primary", width="stretch", key="retry_generation"):
                st.session_state["generation_error"] = ""
                st.session_state["pending_generate"] = True
                st.rerun()
        with back_col:
            if st.button("←  Back to Style", width="stretch", key="error_back_style"):
                st.session_state["current_step"] = 2
                st.rerun()
        return

    if path and Path(path).exists():
        _render_result()
        return

    with st.container(border=True):
        st.markdown('<div class="card-title">Ready to generate</div><div class="card-subtitle">EstateFrame will render your selected photos, captions, transitions and optional audio into an MP4.</div>', unsafe_allow_html=True)
        if st.button("Generate Video", type="primary", width="stretch", key="generate_final_step"):
            st.session_state["pending_generate"] = True
            st.session_state["generation_error"] = ""
            st.rerun()
        if st.button("←  Back to Style", key="generate_back_style"):
            st.session_state["current_step"] = 2
            st.rerun()


def _render_create_video() -> None:
    step = int(st.session_state.get("current_step", 0))
    step = max(0, min(step, 3))
    title = "Video Result" if step == 3 and st.session_state.get("last_output_path") else "Create New Video"
    subtitle = [
        "Enter the property details you want to show in the video.",
        "Upload and order the photos used in the video scenes.",
        "Choose a style and review the narration before export.",
        "Generate, preview and download the finished MP4.",
    ][step]
    st.markdown(f'<div class="page-eyebrow">ESTATEFRAME STUDIO</div><h1>{title}</h1><p class="page-subtitle">{subtitle}</p>', unsafe_allow_html=True)
    _render_stepper(step)
    if step == 0:
        _render_details_step()
    elif step == 1:
        _render_photos_step()
    elif step == 2:
        _render_style_step()
    else:
        _render_generate_step()


def _render_history() -> None:
    st.markdown('<div class="page-eyebrow">YOUR WORKSPACE</div><h1>My Videos</h1><p class="page-subtitle">Videos generated during this session.</p>', unsafe_allow_html=True)
    history = st.session_state.get("history", [])
    if not history:
        with st.container(border=True):
            st.markdown("### No videos generated yet")
            st.markdown('<div class="muted-note">Your exported videos will appear here for this session.</div>', unsafe_allow_html=True)
            if st.button("Create New Video", type="primary", key="history_create"):
                st.session_state["current_step"] = 0
                _go_to("Create Video")
        return
    for idx, item in enumerate(history):
        path = Path(item.get("path", ""))
        if not path.exists():
            continue
        with st.container(border=True):
            col_video, col_detail, col_actions = st.columns([1.15, 1.25, .75], gap="medium", vertical_alignment="center")
            with col_video:
                st.video(str(path))
            with col_detail:
                st.markdown(f"**{html.escape(item.get('name', 'Property video'))}**")
                st.caption(item.get("location", ""))
                st.caption(f"Created {item.get('created_at', 'this session')}")
                meta = item.get("meta", {})
                st.caption(f"{meta.get('duration_seconds', '—')} sec · {meta.get('resolution', '—')} · {meta.get('file_size_mb', '—')} MB")
            with col_actions:
                st.download_button("Download MP4", data=path.read_bytes(), file_name=path.name, mime="video/mp4", type="primary", width="stretch", key=f"history_download_{idx}")
                if st.button("Delete", width="stretch", key=f"history_delete_{idx}"):
                    path.unlink(missing_ok=True)
                    st.session_state["history"].pop(idx)
                    if st.session_state.get("last_output_path") == str(path):
                        st.session_state["last_output_path"] = ""
                        st.session_state["last_output_meta"] = None
                        st.session_state["last_output_details"] = None
                    st.rerun()


def _render_templates() -> None:
    st.markdown('<div class="page-eyebrow">STYLE PRESETS</div><h1>Templates</h1><p class="page-subtitle">Choose a visual direction for your next property video.</p>', unsafe_allow_html=True)
    items = _demo_photo_items()
    cols = st.columns(4, gap="medium")
    for idx, (col, style) in enumerate(zip(cols, STYLE_COPY.keys())):
        with col:
            with st.container(border=True):
                if items:
                    st.image(_image_from_item(items[min(idx, len(items) - 1)]), width="stretch")
                st.markdown(f"### {style}")
                st.markdown(f'<div class="muted-note">{html.escape(STYLE_COPY[style])}</div>', unsafe_allow_html=True)
                st.caption("Selected" if style == st.session_state.get("visual_style") else "Style preset")
                st.button("Use template", key=f"template_{style}", type="primary" if style == st.session_state.get("visual_style") else "secondary", width="stretch", on_click=_apply_template, args=(style,))


def _render_settings() -> None:
    st.markdown('<div class="page-eyebrow">WORKSPACE PREFERENCES</div><h1>Settings</h1><p class="page-subtitle">Set defaults for new property video projects in this session.</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="card-title">Project defaults</div><div class="card-subtitle">These values are applied when loading the sample project during this session.</div>', unsafe_allow_html=True)
        st.text_input("Default brand / agency", key="settings_brand_name", value=st.session_state.get("default_brand_name", "ESTATEFRAME FILMS"))
        st.text_input("Default enquiry text", key="settings_cta", value=st.session_state.get("default_cta", "Enquire today"))
        st.button("Save preferences", type="primary", on_click=_save_preferences, key="save_preferences")
        if st.session_state.get("preferences_saved"):
            st.success("Preferences saved for this session.")


_init_state()
_persist_widget_state()
_ensure_script_draft()
page = _top_nav()

if page == "Home":
    _render_home()
elif page == "Create Video":
    _render_create_video()
elif page == "My Videos":
    _render_history()
elif page == "Templates":
    _render_templates()
elif page == "Settings":
    _render_settings()
