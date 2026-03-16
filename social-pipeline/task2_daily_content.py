#!/usr/bin/env python3
"""Task 2: Daily Content Generator

Generates 3 content pieces daily based on what's performed well in the past.
Sends a single digest email for review.

Schedule: Every day at 8:00 AM (via cron/launchd)
"""

import logging
import random
from datetime import datetime, timezone

from config import CONTENT_PILLARS, STYLE_GUIDE, LOG_DIR
from state_manager import load_state, save_state, generate_post_id, add_performance_entry
from gemini_client import generate_json
from emailer import send_draft_email, format_daily_digest_email

# Logging
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "daily_content.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


FORMATS = [
    {
        "name": "carousel",
        "instruction": """Create a carousel concept with 5-7 slides.
        Slide 1 must be a strong hook that makes people stop scrolling.
        Each subsequent slide should deliver one clear point.
        Final slide should have a CTA.""",
    },
    {
        "name": "single_stat",
        "instruction": """Create a single bold stat or fact post.
        One attention-grabbing claim backed by a brief explanation.
        Should make people want to save or share.""",
    },
    {
        "name": "quick_tip_reel",
        "instruction": """Create a quick tip reel concept.
        Strong hook line, 3 bullet points (actionable tips), and a CTA.
        Format it as a script someone could read to camera in 30-60 seconds.""",
    },
]


def build_context(state: dict) -> str:
    """Build generation context from past performance data."""
    parts = []

    learnings = state.get("weekly_learnings", "")
    if learnings:
        parts.append(f"What's been working recently: {learnings}")

    high_hooks = state.get("hook_patterns", {}).get("high", [])
    if high_hooks:
        parts.append(f"High-performing hook patterns: {', '.join(high_hooks[:5])}")

    low_hooks = state.get("hook_patterns", {}).get("low", [])
    if low_hooks:
        parts.append(f"Hooks to AVOID (underperformed): {', '.join(low_hooks[:3])}")

    top_formats = state.get("top_formats", [])
    if top_formats:
        parts.append(f"Best performing formats: {', '.join(top_formats[:3])}")

    top_topics = state.get("top_topics", [])
    if top_topics:
        parts.append(f"Best performing topics: {', '.join(top_topics[:3])}")

    return "\n".join(parts) if parts else "No past performance data yet. Go with strong fundamentals."


def pick_topics(state: dict) -> list[str]:
    """Pick 3 content pillars, weighting toward top performers."""
    top = state.get("top_topics", [])
    pillars = CONTENT_PILLARS.copy()

    # Bias toward what works, but always include variety
    weighted = []
    for p in pillars:
        weight = 3 if any(t.lower() in p.lower() for t in top) else 1
        weighted.extend([p] * weight)

    selected = []
    for _ in range(3):
        choice = random.choice(weighted)
        selected.append(choice)
        # Remove to avoid exact duplicates
        weighted = [w for w in weighted if w != choice]
        if not weighted:
            weighted = pillars.copy()

    return selected


def generate_content_piece(fmt: dict, topic: str, context: str) -> dict:
    """Generate a single content piece. For carousels, generates per-slide image prompts."""
    if fmt["name"] == "carousel":
        return _generate_carousel(topic, fmt, context)

    prompt = f"""Generate social media content for an AI literacy account.

CONTENT PILLAR: {topic}
FORMAT: {fmt['name']}
{fmt['instruction']}

CONTEXT FROM PAST PERFORMANCE:
{context}

TODAY'S DATE: {datetime.now(timezone.utc).strftime('%B %d, %Y')}

Generate:
1. Full Instagram caption (casual tone, 3-5 hashtags, CTA at the end)
2. Condensed Twitter/X version (under 280 characters, 2-3 hashtags)
3. Image concept (1 sentence — clean, bold, dark background graphic description)

Return JSON:
{{
  "hook": "<the hook line>",
  "topic": "{topic}",
  "format": "{fmt['name']}",
  "ig_caption": "<full instagram caption>",
  "twitter_post": "<280 char twitter version>",
  "image_concept": "<1 sentence image description>",
  "slides": []
}}
"""
    return generate_json(prompt)


def _generate_carousel(topic: str, fmt: dict, context: str) -> dict:
    """Generate a carousel with individual image prompts per slide."""
    # Step 1: Generate the carousel structure and copy
    structure_prompt = f"""Generate an Instagram carousel for an AI literacy account.

CONTENT PILLAR: {topic}
{fmt['instruction']}

CONTEXT FROM PAST PERFORMANCE:
{context}

TODAY'S DATE: {datetime.now(timezone.utc).strftime('%B %d, %Y')}

Generate the carousel structure and captions. Each slide needs:
- headline: Bold text for the slide (10 words max)
- body: 1-2 supporting lines (optional, skip for hook/CTA slides)

Also generate the Instagram caption and Twitter post.

Return JSON:
{{
  "hook": "<the hook line from slide 1>",
  "topic": "{topic}",
  "format": "carousel",
  "slides": [
    {{"slide_number": 1, "headline": "<hook text>", "body": ""}},
    {{"slide_number": 2, "headline": "<point>", "body": "<detail>"}},
    ...
  ],
  "ig_caption": "<full instagram caption with 3-5 hashtags and CTA>",
  "twitter_post": "<under 280 chars, 2-3 hashtags>"
}}
"""
    result = generate_json(structure_prompt)

    # Step 2: Generate an individual image prompt for each slide
    slides = result.get("slides", [])
    image_prompts = []
    for slide in slides:
        img_prompt = f"""Write a detailed image generation prompt for one slide of an Instagram carousel.

CAROUSEL TOPIC: {topic}
SLIDE {slide.get('slide_number', '?')} OF {len(slides)}
HEADLINE TEXT ON SLIDE: {slide.get('headline', '')}
BODY TEXT ON SLIDE: {slide.get('body', '')}

Design constraints:
- Dark background (black or near-black)
- Bold white sans-serif headline text
- Accent color for emphasis (electric blue, neon green, or warm orange)
- Clean, minimal layout — no clutter
- 1080x1080 Instagram square format
- Text must be readable and prominent
- If relevant, include a simple icon or illustration (flat style, not 3D)

Write a single image generation prompt (2-3 sentences) that an AI image tool could use to create this slide. Be specific about layout, colors, and visual elements.

Return JSON:
{{"slide_number": {slide.get('slide_number', 0)}, "image_prompt": "<the prompt>"}}
"""
        try:
            img_result = generate_json(img_prompt)
            image_prompts.append(img_result)
        except Exception as e:
            logger.warning(f"Failed to generate image prompt for slide {slide.get('slide_number')}: {e}")
            image_prompts.append({
                "slide_number": slide.get("slide_number", 0),
                "image_prompt": f"Dark background, bold white text: '{slide.get('headline', '')}'. Minimal, clean design. 1080x1080.",
            })

    result["image_prompts"] = image_prompts
    return result


def run():
    logger.info("=== Daily Content Generator starting ===")
    state = load_state()
    context = build_context(state)
    topics = pick_topics(state)

    logger.info(f"Today's topics: {topics}")
    logger.info(f"Context: {context[:200]}...")

    posts = []
    for i, (fmt, topic) in enumerate(zip(FORMATS, topics)):
        logger.info(f"Generating post {i+1}: {fmt['name']} on '{topic}'")
        try:
            post = generate_content_piece(fmt, topic, context)
            posts.append(post)

            # Track in state
            post_id = generate_post_id()
            state["sent_post_ids"].append(post_id)
            for platform in ["instagram", "twitter"]:
                add_performance_entry(
                    state, post_id, platform,
                    post.get("hook", ""),
                    post.get("format", fmt["name"]),
                    post.get("topic", topic),
                )
            logger.info(f"  ✓ Generated: {post.get('hook', '')[:60]}")
        except Exception as e:
            logger.error(f"  ✗ Failed to generate post {i+1}: {e}")

    if posts:
        # Send digest email
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        html = format_daily_digest_email(posts)
        send_draft_email(
            subject=f"[DAILY CONTENT] {date_str} — {len(posts)} posts ready for review",
            html_body=html,
        )
        logger.info(f"Digest email sent with {len(posts)} posts")
    else:
        logger.warning("No posts generated. Skipping email.")

    save_state(state)
    logger.info("=== Daily Content Generator done ===")


if __name__ == "__main__":
    run()
