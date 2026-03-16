#!/usr/bin/env python3
"""Task 1: Breaking News Monitor

Polls AI-focused RSS feeds, scores stories for relevance/virality,
generates social media drafts for high-scoring stories, and emails them.

Schedule: Every 30 minutes (via cron/launchd)
"""

import hashlib
import logging
from datetime import datetime, timezone

import feedparser

from config import RSS_FEEDS, STYLE_GUIDE, LOG_DIR
from state_manager import load_state, save_state, generate_post_id, add_performance_entry
from gemini_client import generate, generate_json
from emailer import send_draft_email, format_breaking_news_email

# Logging
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "news_monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def make_item_id(item: dict) -> str:
    """Create a stable ID from an RSS item."""
    raw = item.get("id", "") or item.get("link", "") or item.get("title", "")
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def matches_ai_filter(item: dict, filter_tags: list[str]) -> bool:
    """Check if an RSS item is AI-related based on title/summary/tags."""
    if not filter_tags:
        return True  # No filter = all items relevant (e.g., OpenAI blog)

    searchable = " ".join([
        item.get("title", ""),
        item.get("summary", ""),
        " ".join(t.get("term", "") for t in item.get("tags", [])),
    ]).lower()

    return any(tag in searchable for tag in filter_tags)


def score_story(title: str, summary: str) -> dict:
    """Use Gemini to score a story 1-10 for relevance and virality."""
    prompt = f"""Score this AI news story for a social media account focused on making AI accessible to everyday adults.

Title: {title}
Summary: {summary[:500]}

Score it 1-10 on two dimensions:
- relevance: How relevant is this to non-technical adults who want to understand AI's impact on their lives?
- virality: How likely is this to get engagement (saves, shares, comments) on Instagram/Twitter?

Return JSON: {{"relevance": <int>, "virality": <int>, "combined": <int>, "reason": "<1 sentence>"}}
"""
    try:
        result = generate_json(prompt, system_instruction="You are an AI news analyst scoring stories for social media potential.")
        return result
    except Exception as e:
        logger.warning(f"Failed to score story: {e}")
        return {"relevance": 5, "virality": 5, "combined": 5, "reason": "Scoring failed, using default"}


def generate_posts(title: str, summary: str, link: str, state: dict) -> dict:
    """Generate Twitter and Instagram posts for a high-scoring story."""
    # Build context from past learnings
    learnings = state.get("weekly_learnings", "")
    high_hooks = state.get("hook_patterns", {}).get("high", [])

    context = ""
    if learnings:
        context += f"\nPast learnings about what works: {learnings}\n"
    if high_hooks:
        context += f"\nHigh-performing hook styles: {', '.join(high_hooks[:5])}\n"

    prompt = f"""You're writing social media posts about this breaking AI news:

Title: {title}
Summary: {summary[:800]}
Link: {link}
{context}

Generate:
1. A Twitter/X post: Strong hook + 1-2 sentences + 2-3 relevant hashtags. MUST be under 280 characters total.
2. An Instagram caption: Expanded version, casual tone, 3-5 hashtags, end with a CTA like "Save this" or "Tag someone who needs to know this."
3. An image concept: One sentence describing a clean, bold graphic to accompany the post (dark background, bold typography, minimal design).

Return JSON:
{{
  "twitter_post": "<280 char post>",
  "ig_caption": "<full instagram caption>",
  "image_concept": "<1 sentence image description>",
  "hook": "<the hook phrase used>"
}}
"""
    return generate_json(prompt)


def run():
    logger.info("=== News Monitor starting ===")
    state = load_state()
    seen_ids = set(state.get("rss_seen_ids", []))
    new_stories = []

    # Poll all feeds
    for feed_config in RSS_FEEDS:
        url = feed_config["url"]
        filter_tags = feed_config["filter_tags"]
        logger.info(f"Polling: {url}")

        try:
            feed = feedparser.parse(url)
        except Exception as e:
            logger.error(f"Failed to parse {url}: {e}")
            continue

        for item in feed.entries[:15]:  # Check latest 15 per feed
            item_id = make_item_id(item)
            if item_id in seen_ids:
                continue

            if not matches_ai_filter(item, filter_tags):
                seen_ids.add(item_id)
                continue

            new_stories.append({
                "id": item_id,
                "title": item.get("title", "Untitled"),
                "summary": item.get("summary", ""),
                "link": item.get("link", ""),
                "source": feed.feed.get("title", url),
                "published": item.get("published", ""),
            })
            seen_ids.add(item_id)

    logger.info(f"Found {len(new_stories)} new AI stories across all feeds")

    # Score and process stories
    drafted = 0
    for story in new_stories:
        scores = score_story(story["title"], story["summary"])
        story["score"] = scores.get("combined", 5)
        logger.info(f"  [{story['score']}/10] {story['title'][:80]}")

        if story["score"] >= 7:
            logger.info(f"  → High score! Generating posts...")
            try:
                posts = generate_posts(story["title"], story["summary"], story["link"], state)

                # Send email
                html = format_breaking_news_email(
                    story,
                    posts["twitter_post"],
                    posts["ig_caption"],
                    posts["image_concept"],
                )
                send_draft_email(
                    subject=f"[BREAKING] {story['title'][:80]}",
                    html_body=html,
                )

                # Track in state
                post_id = generate_post_id()
                state["sent_post_ids"].append(post_id)
                add_performance_entry(
                    state, post_id, "twitter",
                    posts.get("hook", story["title"][:50]),
                    "breaking_news", "breaking_ai_news",
                )
                add_performance_entry(
                    state, post_id, "instagram",
                    posts.get("hook", story["title"][:50]),
                    "breaking_news", "breaking_ai_news",
                )
                drafted += 1
            except Exception as e:
                logger.error(f"  → Failed to generate/send: {e}")

    # Save state
    state["rss_seen_ids"] = list(seen_ids)
    save_state(state)
    logger.info(f"=== News Monitor done. {drafted} drafts sent. ===")


if __name__ == "__main__":
    run()
