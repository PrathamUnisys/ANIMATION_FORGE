from __future__ import annotations

import io
from typing import Any

from .common import sha256_text

CANVAS = 1024


def _camera_position(shot_type: str) -> tuple[float, float, float]:
    """Return normalized camera x, y and focus depth for a shot type."""
    lowered = (shot_type or "medium").lower()
    if "wide" in lowered or "establish" in lowered:
        return 0.50, 0.97, 0.32
    if "close" in lowered:
        return 0.50, 0.92, 0.52
    if "high" in lowered or "overhead" in lowered:
        return 0.50, 0.95, 0.40
    return 0.50, 0.95, 0.42


def _character_positions(characters: list[str]) -> list[dict[str, Any]]:
    count = len(characters)
    if count == 0:
        return []
    if count == 1:
        offsets = [0.0]
    elif count == 2:
        offsets = [-0.16, 0.16]
    elif count == 3:
        offsets = [-0.24, 0.0, 0.24]
    else:
        span = 0.72
        step = span / (count - 1)
        offsets = [-span / 2 + step * index for index in range(count)]
    placements = []
    for index, name in enumerate(characters):
        placements.append(
            {
                "name": name,
                "x": round(0.5 + offsets[index], 4),
                "y": round(0.45 if count > 1 else 0.44, 4),
                "radius": 0.045,
                "facing": "toward_camera",
            }
        )
    return placements


def _prop_positions(props: list[str]) -> list[dict[str, Any]]:
    placements = []
    for index, name in enumerate(props):
        placements.append(
            {
                "name": name,
                "x": round(0.22 + 0.56 * (index / max(len(props) - 1, 1)), 4),
                "y": 0.74,
                "size": 0.05,
            }
        )
    return placements


def build_blocking_layout(shot: dict[str, Any], scene: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic normalized plan-view staging layout.

    All coordinates are normalized to a 0..1 stage rectangle. They describe
    relative staging only and are not Blender or Unreal world coordinates.
    """
    characters = list(shot.get("characters", []))
    props = list(shot.get("props", []))
    camera_x, camera_y, focus_y = _camera_position(shot.get("camera_shot_type", "medium"))
    character_layout = _character_positions(characters)
    focus = character_layout[0] if character_layout else {"x": 0.5, "y": focus_y}
    return {
        "shot_id": shot.get("shot_id", ""),
        "scene_id": scene.get("scene_id", ""),
        "coordinate_space": "NORMALIZED_STAGE_0_TO_1",
        "not_world_coordinates": True,
        "stage": {"x": 0.06, "y": 0.04, "width": 0.88, "height": 0.80},
        "camera": {
            "x": camera_x,
            "y": camera_y,
            "fov_deg": {"wide": 55.0, "medium": 40.0, "close-up": 28.0}.get(
                (shot.get("camera_shot_type") or "medium").lower(), 40.0
            ),
            "focus_x": focus["x"],
            "focus_y": focus["y"],
            "sightline": True,
        },
        "characters": character_layout,
        "props": _prop_positions(props),
        "movement": {
            "direction": "upstage_left_to_right" if characters else "static",
            "note": "Movement direction is inferred from shot content, not measured.",
        },
        "environment": scene.get("location", ""),
        "inferred": True,
        "notes": [
            "Positions are relative staging decisions inferred from the shot description.",
            "This layout is not a validated 3D scene and carries no scale or unit.",
        ],
    }


def _px(value: float, canvas: int) -> float:
    return round(value * canvas, 2)


def render_blocking_svg(layout: dict[str, Any], canvas: int = CANVAS) -> str:
    """Render the plan view as an SVG vector deliverable."""
    stage = layout["stage"]
    camera = layout["camera"]
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas}" height="{canvas}" '
        f'viewBox="0 0 {canvas} {canvas}">',
        '<rect width="100%" height="100%" fill="#12161c"/>',
        f'<rect x="{_px(stage["x"], canvas)}" y="{_px(stage["y"], canvas)}" '
        f'width="{_px(stage["width"], canvas)}" height="{_px(stage["height"], canvas)}" '
        'fill="#1b2129" stroke="#4c5a6b" stroke-width="3" stroke-dasharray="10 6"/>',
        f'<text x="16" y="34" fill="#9fb0c4" font-family="sans-serif" font-size="22">'
        f'{layout["shot_id"]} &#183; {layout["scene_id"]} &#183; normalized plan view</text>',
    ]

    camera_x = _px(camera["x"], canvas)
    camera_y = _px(camera["y"], canvas)
    focus_x = _px(camera["focus_x"], canvas)
    focus_y = _px(camera["focus_y"], canvas)
    spread = canvas * 0.26
    parts.append(
        f'<polygon points="{camera_x},{camera_y} {focus_x - spread:.1f},{focus_y + spread:.1f} '
        f'{focus_x + spread:.1f},{focus_y + spread:.1f}" fill="#f2c14e" fill-opacity="0.12"/>'
    )
    parts.append(
        f'<line x1="{camera_x}" y1="{camera_y}" x2="{focus_x}" y2="{focus_y}" '
        'stroke="#f2c14e" stroke-width="3" stroke-dasharray="8 6"/>'
    )
    parts.append(
        f'<polygon points="{camera_x - 20},{camera_y + 34} {camera_x + 20},{camera_y + 34} '
        f'{camera_x},{camera_y - 18}" fill="#f2c14e"/>'
    )
    parts.append(
        f'<text x="{camera_x + 28}" y="{camera_y + 28}" fill="#f2c14e" '
        'font-family="sans-serif" font-size="20">camera</text>'
    )

    for character in layout["characters"]:
        cx = _px(character["x"], canvas)
        cy = _px(character["y"], canvas)
        radius = _px(character["radius"], canvas)
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="#7fd1b9" fill-opacity="0.85" '
            'stroke="#12161c" stroke-width="3"/>'
        )
        initials = "".join(part[0] for part in character["name"].split()[:2]).upper()
        parts.append(
            f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" fill="#0d1117" '
            f'font-family="sans-serif" font-size="26" font-weight="bold">{initials}</text>'
        )
        parts.append(
            f'<text x="{cx}" y="{cy + radius + 26}" text-anchor="middle" fill="#d8e2ee" '
            f'font-family="sans-serif" font-size="19">{character["name"]}</text>'
        )

    for prop in layout["props"]:
        px = _px(prop["x"], canvas)
        py = _px(prop["y"], canvas)
        half = _px(prop["size"], canvas) / 2
        parts.append(
            f'<rect x="{px - half}" y="{py - half}" width="{half * 2}" height="{half * 2}" '
            'fill="#c98b5e" fill-opacity="0.9" stroke="#12161c" stroke-width="3"/>'
        )
        parts.append(
            f'<text x="{px}" y="{py + half + 22}" text-anchor="middle" fill="#d8e2ee" '
            f'font-family="sans-serif" font-size="17">{prop["name"]}</text>'
        )

    parts.append(
        f'<text x="16" y="{canvas - 18}" fill="#6f8098" font-family="sans-serif" font-size="17">'
        'Normalized staging only - not Blender/Unreal coordinates, no scale or unit.</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def render_blocking_png(layout: dict[str, Any], canvas: int = CANVAS) -> bytes:
    """Render the plan view as a PNG for direct inspection and ControlNet use."""
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (canvas, canvas), (18, 22, 28))
    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 26)
        label_font = ImageFont.truetype("arial.ttf", 21)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        title_font = label_font = small_font = ImageFont.load_default()

    stage = layout["stage"]
    camera = layout["camera"]

    draw.rectangle(
        [
            _px(stage["x"], canvas),
            _px(stage["y"], canvas),
            _px(stage["x"] + stage["width"], canvas),
            _px(stage["y"] + stage["height"], canvas),
        ],
        fill=(27, 33, 41),
        outline=(76, 90, 107),
        width=3,
    )

    camera_x = _px(camera["x"], canvas)
    camera_y = _px(camera["y"], canvas)
    focus_x = _px(camera["focus_x"], canvas)
    focus_y = _px(camera["focus_y"], canvas)
    spread = canvas * 0.26

    image_draw_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(image_draw_overlay)
    overlay_draw.polygon(
        [
            (camera_x, camera_y),
            (focus_x - spread, focus_y + spread),
            (focus_x + spread, focus_y + spread),
        ],
        fill=(242, 193, 78, 40),
    )
    overlay_draw.polygon(
        [
            (camera_x, camera_y),
            (focus_x - spread, focus_y + spread),
            (focus_x + spread, focus_y + spread),
        ],
        outline=(242, 193, 78, 220),
        width=3,
    )
    image = Image.alpha_composite(image.convert("RGBA"), image_draw_overlay).convert("RGB")
    draw = ImageDraw.Draw(image)

    draw.line((camera_x, camera_y, focus_x, focus_y), fill=(242, 193, 78), width=3)
    draw.polygon(
        [(camera_x - 22, camera_y + 36), (camera_x + 22, camera_y + 36), (camera_x, camera_y - 20)],
        fill=(242, 193, 78),
    )
    draw.text((camera_x + 30, camera_y + 16), "camera", fill=(242, 193, 78), font=label_font)

    for character in layout["characters"]:
        cx = _px(character["x"], canvas)
        cy = _px(character["y"], canvas)
        radius = _px(character["radius"], canvas)
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(127, 209, 185),
            outline=(18, 22, 28),
            width=3,
        )
        initials = "".join(part[0] for part in character["name"].split()[:2]).upper()
        draw.text((cx, cy - 12), initials, fill=(13, 17, 23), font=title_font)
        draw.text(
            (cx - 60, cy + radius + 8), character["name"], fill=(216, 226, 238), font=label_font
        )

    for prop in layout["props"]:
        px = _px(prop["x"], canvas)
        py = _px(prop["y"], canvas)
        half = _px(prop["size"], canvas) / 2
        draw.rectangle(
            [px - half, py - half, px + half, py + half],
            fill=(201, 139, 94),
            outline=(18, 22, 28),
            width=3,
        )
        draw.text((px - 50, py + half + 6), prop["name"], fill=(216, 226, 238), font=small_font)

    draw.text(
        (16, 14),
        f'{layout["shot_id"]} - {layout["scene_id"]} - normalized plan view',
        fill=(159, 176, 196),
        font=title_font,
    )
    draw.text(
        (16, canvas - 30),
        "Normalized staging only - not Blender/Unreal coordinates, no scale or unit.",
        fill=(111, 128, 152),
        font=small_font,
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def layout_hash(layout: dict[str, Any]) -> str:
    return sha256_text(repr(layout))
