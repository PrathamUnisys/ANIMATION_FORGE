from __future__ import annotations

from typing import Any

from .common import new_id, utc_now

STYLE_PROFILES: list[dict[str, Any]] = [
    {
        "style_name": "Cinematic Realism",
        "description": "Grounded live-action cinematography with naturalistic light and measurable depth.",
        "prompt_suffix": (
            "cinematic realism, live-action feature film still, naturalistic lighting, "
            "anamorphic lens, shallow depth of field, film grain, physically plausible materials"
        ),
        "palette": "Desaturated earth tones with warm amber highlights and cool shadow fill.",
        "lighting": "Motivated three-point cinematic lighting; soft key, practical sources, gentle rim.",
        "materials": "Worn stone, oxidized bronze, damp moss, woven cloth; believable surface wear.",
        "geometry": "Real-world proportions and perspective; no exaggerated anatomy.",
        "environment": "Architectural scale readable from foreground to background; atmospheric haze.",
        "character_design": "Human-proportioned squire; translucent slime familiar with internal refraction.",
        "camera": "35mm anamorphic, eye-level coverage, restrained movement.",
        "composition": "Depth-staged wides and mediums with subjects held off centre; foreground occlusion used sparingly.",
        "atmosphere": "Grounded and unsentimental; real air and real weather, no stylisation of the mood.",
        "storytelling": "Performance and spatial relationships drive the frame.",
        "feasibility": "High for Blender/Unreal; needs believable textures and character rigs.",
        "generation_requirements": "Checkpoint only; no control net required.",
        "strengths": ["Strong production readability", "Easy engine translation"],
        "limitations": ["Less stylized; may read generic without strong art direction"],
    },
    {
        "style_name": "Stylized 3D Animation",
        "description": "Pixar-style dimensional staging with appealing shapes and readable silhouettes.",
        "prompt_suffix": (
            "stylized 3D animation, feature animation still, appealing shapes, clean silhouettes, "
            "soft global illumination, subsurface scattering, vibrant but controlled palette"
        ),
        "palette": "Saturated primaries balanced by neutral stone; teal-and-amber contrast.",
        "lighting": "Soft key with broad fill, colored bounce, gentle rim for silhouette separation.",
        "materials": "Slightly exaggerated surface response; moss reads as soft velvet, metal as toy-like.",
        "geometry": "Rounded, appealing forms; proportions slightly compressed for charm.",
        "environment": "Readable stage-like space with clear foreground, midground and background planes.",
        "character_design": "Appealing cartoon proportions; expressive eyes and readable gestures.",
        "camera": "50mm-equivalent, slightly low camera for hero staging, smooth moves.",
        "composition": "Hero staging on a readable stage; foreground, midground and background kept apart for silhouette clarity.",
        "atmosphere": "Warm and inviting; the world feels handled and lit rather than observed.",
        "storytelling": "Shape language and color carry the joke and the beat.",
        "feasibility": "High for Blender/Unreal stylized pipelines; needs toon or stylized shaders.",
        "generation_requirements": "Checkpoint plus optional stylized LoRA.",
        "strengths": ["Highly readable at thumbnail size", "Strong character appeal"],
        "limitations": ["Requires shader work to match in engine"],
    },
    {
        "style_name": "Miniature Diorama",
        "description": "A hand-built tabletop world with tilt-shift depth and practical textures.",
        "prompt_suffix": (
            "miniature diorama, tabletop model photography, tilt-shift lens, practical miniature, "
            "hand-painted textures, forced perspective, soft studio light"
        ),
        "palette": "Muted craft-store colors with selective bright accents on props.",
        "lighting": "Large soft source from above; subtle practicals; tilt-shift falloff.",
        "materials": "Foam, clay, paper, painted wood; visible but tasteful craft texture.",
        "geometry": "Slightly compressed depth; architectural details simplified but layered.",
        "environment": "A contained stage that reads as a built set with visible edges.",
        "character_design": "Maquette-style figures with sculpted clothing and simplified faces.",
        "camera": "Tilt-shift macro, high angle or low hero angle, shallow depth.",
        "composition": "High or low three-quarter views that show the whole tabletop set; tilt-shift keeps the edges soft.",
        "atmosphere": "Small, crafted and precious; the scene reads as an object held in a hand.",
        "storytelling": "The set itself is a character; scale and craft communicate tone.",
        "feasibility": "Good for previs; engine version needs modular kit assets.",
        "generation_requirements": "Checkpoint only; optional LoRA for craft texture.",
        "strengths": ["Distinctive, charming, highly reproducible", "Clear spatial read"],
        "limitations": ["Harder to make dramatic; craft look may not suit all genres"],
    },
    {
        "style_name": "Painterly Environments",
        "description": "Traditional oil-painting language with visible brushwork and atmospheric depth.",
        "prompt_suffix": (
            "painterly environment art, oil painting, visible brushwork, atmospheric perspective, "
            "classical composition, rich impasto highlights, moody chiaroscuro"
        ),
        "palette": "Warm ochre, umber, deep green, and muted gold; limited but harmonious.",
        "lighting": "Chiaroscuro with a single dominant source; soft atmospheric falloff.",
        "materials": "Paint handling suggests stone, metal and slime rather than describing them.",
        "geometry": "Classical perspective; forms simplified into value masses.",
        "environment": "Layered depth with foreground framing elements and hazy background.",
        "character_design": "Painted figures with strong value shapes and minimal interior line.",
        "camera": "Painted-frame composition; classical thirds and foreground framing.",
        "composition": "Classical thirds with painted foreground framing and a deep atmospheric recession.",
        "atmosphere": "Quiet and considered; mood carried by brushwork, haze and warm-to-cool transitions.",
        "storytelling": "Mood and value structure carry narrative emphasis.",
        "feasibility": "Excellent concept reference; engine version needs matching texture language.",
        "generation_requirements": "Checkpoint plus painterly LoRA if available.",
        "strengths": ["Strong mood and memorable key art", "Good for tone alignment"],
        "limitations": ["Loose detail can conflict with precise production needs"],
    },
    {
        "style_name": "Graphic Novel Noir",
        "description": "High-contrast ink illustration with bold shapes and limited flat color.",
        "prompt_suffix": (
            "graphic novel art, noir comic illustration, bold ink outlines, high-contrast shadows, "
            "limited flat color palette, halftone texture, dynamic panel composition"
        ),
        "palette": "Black, bone white, emerald green, and one amber accent.",
        "lighting": "Hard graphic shadows; light rendered as negative space.",
        "materials": "Ink and flat color; texture implied by line weight and pattern.",
        "geometry": "Slightly exaggerated poses; strong silhouettes and forced perspective.",
        "environment": "Architectural shapes reduced to bold graphic masses.",
        "character_design": "Expressive ink figures with readable silhouettes and graphic costumes.",
        "camera": "Dynamic angles, Dutch tilts, dramatic foreshortening.",
        "composition": "Hard graphic framing, high camera angles, bold shapes and large areas of negative space.",
        "atmosphere": "Tense and shadow-heavy; information is withheld and revealed by contrast.",
        "storytelling": "Panel-like framing; each image is a story beat.",
        "feasibility": "Great for shot flow and readability; engine version needs toon shading.",
        "generation_requirements": "Checkpoint plus graphic-novel LoRA if available.",
        "strengths": ["Extremely readable story beats", "Strong consistent identity"],
        "limitations": ["Limited tonal subtlety; may need post to match in engine"],
    },
    {
        "style_name": "Stop-Motion Aesthetic",
        "description": "Frame-by-frame puppet animation with tactile sets and intentional imperfection.",
        "prompt_suffix": (
            "stop-motion animation, puppet film still, tactile miniature set, visible fingerprints in clay, "
            "practical lighting, slight motion blur, handcrafted texture"
        ),
        "palette": "Dusty, slightly faded colors with warm tungsten practicals.",
        "lighting": "Visible practical lamps and soft key; shadows have a handmade quality.",
        "materials": "Clay, fabric, fur, metal foil; real textures photographed under light.",
        "geometry": "Slightly chunky proportions; joints and armature implied.",
        "environment": "Full practical sets with visible seams and construction.",
        "character_design": "Puppets with replacement faces or expressive sculpted features.",
        "camera": "18mm-ish wide coverage or 35mm medium; locked-off or gentle motion.",
        "composition": "Locked-off or gently moving wide-to-medium coverage; subjects placed squarely in frame.",
        "atmosphere": "Tactile and handmade; visible practical lamps and slight irregularity in every surface.",
        "storytelling": "Physical performance and tactile detail create charm.",
        "feasibility": "Good for previs; engine version needs puppet-style rigs and shaders.",
        "generation_requirements": "Checkpoint only.",
        "strengths": ["Warm, distinctive, highly consistent", "Strong material read"],
        "limitations": ["Slower to interpret for realistic engine pipelines"],
    },
    {
        "style_name": "Documentary Visualization",
        "description": "Informational realism with clear diagrams, labels and explainer staging.",
        "prompt_suffix": (
            "documentary visualization, educational explainer still, clean informative composition, "
            "neutral lighting, clear silhouettes, subtle annotations, realistic rendering"
        ),
        "palette": "Neutral grays and browns with a single informative accent color.",
        "lighting": "Even, shadow-minimizing light for clarity; no dramatic contrast.",
        "materials": "Accurate material reads; surfaces are legible rather than expressive.",
        "geometry": "True proportions and clear spatial relationships.",
        "environment": "Uncluttered staging that isolates the subject and action.",
        "character_design": "Clear, neutral character reads with accurate costume detail.",
        "camera": "Locked-off, eye-level or slightly elevated; diagram-friendly framing.",
        "composition": "Locked-off or slightly elevated framing that leaves clear room for diagram labels and callouts.",
        "atmosphere": "Clear, neutral and instructional; the tone is explanatory rather than dramatic.",
        "storytelling": "Clarity first; every visual element explains rather than decorates.",
        "feasibility": "Excellent for blocking and production planning.",
        "generation_requirements": "Checkpoint only.",
        "strengths": ["Best production readability", "Clear blocking and continuity"],
        "limitations": ["Least emotionally expressive; may feel dry"],
    },
    {
        "style_name": "Low-Poly Stylization",
        "description": "Faceted geometric forms with flat shading and bold color blocking.",
        "prompt_suffix": (
            "low-poly 3D stylization, faceted geometry, flat shading, bold color blocking, "
            "geometric shapes, clean isometric-inspired composition, stylized game art"
        ),
        "palette": "Limited palette of 6-8 bold colors; strong value separation.",
        "lighting": "Flat or simple two-tone shading; no realistic falloff.",
        "materials": "Faceted surfaces; material read through color and shape, not texture.",
        "geometry": "Simplified planar forms; readable silhouettes at low detail.",
        "environment": "Geometric architecture with clear planes and depth layers.",
        "character_design": "Faceted characters with bold readable shapes and simple faces.",
        "camera": "Slightly elevated three-quarter view; clean composition.",
        "composition": "Slightly elevated three-quarter views with bold colour blocking and large clean shapes.",
        "atmosphere": "Graphic and design-flat; contrast comes from colour blocks rather than shadow.",
        "storytelling": "Shape and color communicate action and hierarchy.",
        "feasibility": "Very high for real-time Unreal/Blender; cheap to build.",
        "generation_requirements": "Checkpoint only.",
        "strengths": ["Fastest engine translation", "Highly consistent and readable"],
        "limitations": ["Limited detail; may undersell dramatic moments"],
    },
]


COMPARISON_NEGATIVE_PROMPT = (
    "split panel, multiple panels, comic layout, collage, diptych, triptych, "
    "storyboard sheet, grid of images, multiple views, collage, border, frame, "
    "extra characters, watermark, text, logo, blurry, low resolution, poor anatomy"
)

SINGLE_FRAME_CONSTRAINT = (
    "single continuous frame, one shot only, full-bleed image, no split panels, "
    "no collage, no grid, no borders"
)


def comparison_subject(scene: dict[str, Any]) -> str:
    """Build one concrete, single-frame subject for the art-direction comparison.

    The whole scene action is deliberately not used: a multi-sentence direction
    makes the model produce a split-panel layout, which would make the candidates
    differ by composition instead of by direction.
    """
    shots = scene.get("shots") or []
    source = ""
    if shots:
        source = shots[0].get("visual_description", "")
    if not source:
        source = scene.get("action", "")
    subject = source.split(". ")[0].strip().rstrip(".")
    parts = [subject] if subject else []
    location = scene.get("location")
    if location:
        parts.append(location)
    characters = scene.get("characters", [])
    if characters:
        parts.append(", ".join(characters))
    props = scene.get("props", [])
    if props:
        parts.append(", ".join(props))
    return ", ".join(parts)


def _scene_description(scene: dict[str, Any]) -> str:
    heading = scene.get("heading") or "an unspecified interior space"
    location = scene.get("location") or "the same continuous space"
    time = scene.get("time") or "continuous"
    parts = [f"{heading}.", f"The scene is set in {location} ({time})."]
    characters = scene.get("characters", [])
    if characters:
        parts.append(f"Characters present: {', '.join(characters)}.")
    props = scene.get("props", [])
    if props:
        parts.append(f"Visible props: {', '.join(props)}.")
    subject = comparison_subject(scene)
    if subject:
        parts.append(f"The frame shows: {subject}.")
    return " ".join(parts)


def _pick_comparison_scene(analysis: dict[str, Any]) -> dict[str, Any]:
    """Choose the most visually informative scene as the shared comparison frame.

    For a narrated explainer the opening segment is the natural comparison frame:
    it carries the episode's visual promise. For a screenplay the scene with the
    most characters, props and shots is used.
    """
    if analysis.get("source_format") == "NARRATOR" and analysis.get("sequences"):
        first = analysis["sequences"][0]
        if first.get("scenes"):
            return first["scenes"][0]
    best = None
    best_score = -1
    for sequence in analysis["sequences"]:
        for scene in sequence["scenes"]:
            score = (
                len(scene.get("characters", [])) * 2
                + len(scene.get("props", []))
                + len(scene.get("shots", []))
                + (1 if scene.get("heading") else 0)
            )
            if score > best_score:
                best_score = score
                best = scene
    if best is None:
        raise ValueError("The analysis contains no scenes to use as a comparison frame.")
    return best


def build_candidates(
    analysis: dict[str, Any],
    project_id: str,
    comparison_scene_id: str | None = None,
) -> dict[str, Any]:
    """Build 6-8 distinct art-direction candidates from one shared scene."""
    scene = None
    if comparison_scene_id:
        for sequence in analysis["sequences"]:
            for candidate_scene in sequence["scenes"]:
                if candidate_scene["scene_id"] == comparison_scene_id:
                    scene = candidate_scene
                    break
    if scene is None:
        scene = _pick_comparison_scene(analysis)

    scene_description = _scene_description(scene)
    candidates = []
    for index, profile in enumerate(STYLE_PROFILES, start=1):
        comparison_prompt = (
            f"{profile['prompt_suffix']}. {scene_description} "
            f"{SINGLE_FRAME_CONSTRAINT}, cinematic storybook composition, "
            f"consistent character identity, high detail, production-ready concept art."
        )
        candidates.append(
            {
                "candidate_id": f"ART_{index:02d}",
                "style_name": profile["style_name"],
                "description": profile["description"],
                "style_prompt": profile["prompt_suffix"],
                "comparison_prompt": comparison_prompt,
                "palette": profile["palette"],
                "lighting": profile["lighting"],
                "materials": profile["materials"],
                "geometry": profile["geometry"],
                "environment": profile["environment"],
                "character_design": profile["character_design"],
                "camera": profile["camera"],
                "composition": profile["composition"],
                "atmosphere": profile["atmosphere"],
                "storytelling": profile["storytelling"],
                "feasibility": profile["feasibility"],
                "generation_requirements": profile["generation_requirements"],
                "strengths": profile["strengths"],
                "limitations": profile["limitations"],
                "status": "DRAFT",
                "selected": False,
                "comparison_scene_id": scene["scene_id"],
                "comparison_subject": comparison_subject(scene),
                "comparison_negative_prompt": COMPARISON_NEGATIVE_PROMPT,
            }
        )

    return {
        "schema_version": "1.0.0",
        "candidate_set_id": new_id("ARTSET"),
        "project_id": project_id,
        "analysis_id": analysis["analysis_id"],
        "comparison_scene_id": scene["scene_id"],
        "comparison_seed": 536354036775427,
        "created_at": utc_now(),
        "candidates": candidates,
    }


def select_candidate(candidate_set: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    """Mark exactly one candidate as selected. Never auto-approves a style."""
    selected = None
    for candidate in candidate_set["candidates"]:
        if candidate["candidate_id"] == candidate_id:
            candidate["selected"] = True
            candidate["status"] = "SELECTED"
            selected = candidate
        else:
            candidate["selected"] = False
            if candidate["status"] == "SELECTED":
                candidate["status"] = "DRAFT"
    if selected is None:
        raise ValueError(f"Unknown candidate_id: {candidate_id!r}")
    return candidate_set
