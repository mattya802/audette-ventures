"""Shared configuration for the social media pipeline."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
PIPELINE_DIR = Path(__file__).parent
load_dotenv(PIPELINE_DIR / ".env")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gmail
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
DRAFT_RECIPIENT = os.getenv("DRAFT_RECIPIENT", GMAIL_ADDRESS)

# Instagram (Phase 2)
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

# Paths
STATE_FILE = PIPELINE_DIR / "state.json"
LOG_DIR = PIPELINE_DIR / "logs"

# RSS Feeds to monitor
RSS_FEEDS = [
    {"url": "https://techcrunch.com/feed/", "filter_tags": ["ai", "artificial intelligence", "machine learning", "chatgpt", "openai", "anthropic", "gemini"]},
    {"url": "https://www.theverge.com/rss/index.xml", "filter_tags": ["ai", "artificial intelligence", "machine learning", "chatgpt", "openai", "anthropic"]},
    {"url": "https://openai.com/blog/rss.xml", "filter_tags": []},  # All posts relevant
    {"url": "https://www.anthropic.com/rss.xml", "filter_tags": []},  # All posts relevant
    {"url": "https://feeds.feedburner.com/venturebeat/SZYF", "filter_tags": ["ai", "artificial intelligence", "machine learning"]},
]

# Content pillars for daily generation
CONTENT_PILLARS = [
    "AI tools most people don't know about",
    "Jobs/industries being changed by AI right now",
    "Your kid should know this — AI literacy for parents",
    "Quick wins — something actionable to try tonight",
    "Myth-busting — common AI misconceptions",
]

# Style guide — injected into every generation prompt
STYLE_GUIDE = """
Tone: Casual, direct, founder-voiced. Short sentences. No fluff.
Audience: Adults 25-45 who are AI-curious but not technical. Parents, professionals.
Goal: Make them feel like they're getting insider knowledge they can act on.
Hooks that work: Numbers, curiosity gaps, mild urgency, before/after framing.
Hooks to avoid: Questions as openers, vague inspiration, anything that sounds like a press release.
Never use: "Dive into", "game-changer", "revolutionize", "harness the power of"
Always include: A save or share CTA on Instagram. Hashtags: 3-5 max, relevant not generic.
""".strip()
