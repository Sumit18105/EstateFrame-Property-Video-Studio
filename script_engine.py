"""Template-first copy generation for property promo videos.

All listing-specific claims come only from caller-supplied values. The engine does
not infer amenities, distances, investment returns, legal status, or availability.
"""
from __future__ import annotations

from typing import Any


def parse_features(value: Any) -> list[str]:
    if isinstance(value, str):
        raw = value.replace(";", "\n").replace(",", "\n").splitlines()
    elif isinstance(value, (list, tuple)):
        raw = list(value)
    else:
        raw = []
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in raw:
        text = " ".join(str(item).strip().split()).lstrip("•-–— ").strip()
        key = text.casefold()
        if text and key not in seen:
            cleaned.append(text)
            seen.add(key)
    return cleaned


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def generate_script(details: dict[str, Any]) -> dict[str, Any]:
    """Create voice-over copy, scene captions, and a compact scene plan."""
    name = _clean(details.get("property_name"))
    location = _clean(details.get("location"))
    price = _clean(details.get("price"))
    property_type = _clean(details.get("property_type"))
    cta = _clean(details.get("cta")) or "Enquire today"
    brand = _clean(details.get("brand_name"))
    features = parse_features(details.get("key_features", []))

    narration: list[str] = []
    if name:
        narration.append(name + ".")
    else:
        narration.append("A property showcase.")
    if property_type:
        narration.append(property_type + ".")

    bedrooms = _clean(details.get("bedrooms"))
    bathrooms = _clean(details.get("bathrooms"))
    room_facts: list[str] = []
    if bedrooms and bedrooms not in {"0", "None", "Select"}:
        room_facts.append(f"{bedrooms} bedrooms")
    if bathrooms and bathrooms not in {"0", "None", "Select"}:
        room_facts.append(f"{bathrooms} bathrooms")
    if room_facts:
        narration.append("Includes " + " and ".join(room_facts) + ".")

    area = _clean(details.get("area_sqft"))
    if area and area not in {"0", "None"}:
        try:
            area_label = f"{int(float(area)):,}"
        except (TypeError, ValueError):
            area_label = area
        narration.append(f"Area: {area_label} square feet.")
    if location:
        narration.append("Located in " + location + ".")
    if price:
        narration.append("Listed at " + price + ".")
    description = _clean(details.get("short_description"))
    if description:
        narration.append(description.rstrip(" .") + ".")
    if features:
        narration.append("Key features include " + "; ".join(features) + ".")
    narration.append(cta.rstrip(" .") + ".")

    return {
        "title": name or "Property showcase",
        "location": location,
        "price": price,
        "property_type": property_type,
        "features": features,
        "cta": cta,
        "brand_name": brand,
        "voiceover": " ".join(narration),
        "caption_lines": features,
        "content_policy": "Listing claims use only supplied property details; CTA text is a user-provided or generic prompt.",
    }


def build_scene_plan(details: dict[str, Any], image_count: int) -> list[dict[str, Any]]:
    """Assign supplied images to a cover, feature cards, and an end card."""
    script = generate_script(details)
    safe_count = max(1, min(int(image_count), 8))
    lines = script["features"]
    brand = script["brand_name"] or "PROPERTY FILM"
    name = script["title"]
    location = script["location"]
    property_type = script["property_type"]
    price = script["price"]

    cover_meta = [v for v in (location, property_type) if v]
    scenes: list[dict[str, Any]] = [
        {
            "kind": "cover",
            "image_index": 0,
            "eyebrow": brand,
            "headline": name,
            "subline": "  ·  ".join(cover_meta),
            "tag": "PROPERTY FILM",
        }
    ]
    raw_captions = details.get("scene_captions", [])
    if isinstance(raw_captions, str):
        captions = [" ".join(part.strip().split()) for part in raw_captions.splitlines()]
    elif isinstance(raw_captions, (list, tuple)):
        captions = [" ".join(str(part).strip().split()) for part in raw_captions]
    else:
        captions = []
    for i in range(safe_count):
        if captions:
            caption = captions[i] if i < len(captions) and captions[i] else "A closer look"
        else:
            caption = lines[i] if i < len(lines) else "A closer look"
        context = "  ·  ".join(v for v in (property_type, location) if v)
        scenes.append(
            {
                "kind": "feature",
                "image_index": i,
                "eyebrow": brand,
                "headline": caption,
                "subline": context,
                "tag": f"DETAIL {i + 1:02d} / {safe_count:02d}",
            }
        )
    scenes.append(
        {
            "kind": "outro",
            "image_index": safe_count - 1,
            "eyebrow": brand,
            "headline": script["cta"],
            "subline": "  ·  ".join(v for v in (name, location, price) if v),
            "tag": "ENQUIRIES",
        }
    )
    return scenes
