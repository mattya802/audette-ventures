"""Read/write the persistent state.json file."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config import STATE_FILE

DEFAULT_STATE = {
    "last_run": None,
    "rss_seen_ids": [],
    "sent_post_ids": [],
    "performance": [],
    "hook_patterns": {"high": [], "medium": [], "low": []},
    "top_formats": [],
    "top_topics": [],
    "weekly_learnings": "",
}


def load_state() -> dict:
    if not STATE_FILE.exists():
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE.copy()
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def generate_post_id() -> str:
    return f"post_{uuid.uuid4().hex[:8]}"


def add_performance_entry(
    state: dict,
    post_id: str,
    platform: str,
    hook: str,
    fmt: str,
    topic: str,
) -> dict:
    state["performance"].append({
        "id": post_id,
        "platform": platform,
        "hook": hook,
        "format": fmt,
        "topic": topic,
        "likes": 0,
        "saves": 0,
        "comments": 0,
        "impressions": 0,
        "posted_date": "",
        "score": "pending",
    })
    return state
