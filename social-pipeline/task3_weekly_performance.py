#!/usr/bin/env python3
"""Task 3: Weekly Performance Updater

Two modes:
  --prompt  : Sends a form email asking for last week's performance data
  --update  : Parses performance input and updates state.json

Schedule: Sunday at 9:00 AM (--prompt mode via cron/launchd)
          Run --update manually after replying with data

Usage:
  python task3_weekly_performance.py --prompt
  python task3_weekly_performance.py --update "Post about ChatGPT tips got 500 likes, 200 saves..."
  python task3_weekly_performance.py --update-file performance_notes.txt
"""

import argparse
import logging
from datetime import datetime, timezone

from config import LOG_DIR
from state_manager import load_state, save_state
from gemini_client import generate_json
from emailer import send_draft_email

# Logging
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "performance.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def send_prompt_email():
    """Send the weekly performance check-in email."""
    state = load_state()
    pending = [p for p in state.get("performance", []) if p.get("score") == "pending"]

    post_list = ""
    if pending:
        post_list = "<ul>"
        for p in pending[-20:]:  # Show last 20 pending
            post_list += f"<li><strong>[{p['platform']}]</strong> {p['hook'][:60]} ({p['format']})</li>"
        post_list += "</ul>"
    else:
        post_list = "<p>No pending posts to review.</p>"

    html = f"""
    <h2>📊 Weekly Performance Check-In</h2>
    <p>Hey! Time for the weekly review. Reply to this email (or paste into Claude Desktop) with your notes on last week's posts.</p>

    <h3>Posts awaiting review:</h3>
    {post_list}

    <h3>What I need from you:</h3>
    <ul>
        <li><strong>Top performers:</strong> Which posts got the most likes/saves/engagement? Include numbers if you have them.</li>
        <li><strong>Flops:</strong> Any that clearly underperformed? What do you think went wrong?</li>
        <li><strong>Patterns:</strong> Any trends you noticed? (e.g., "carousels do better than single images", "ChatGPT tips always win")</li>
        <li><strong>Notes:</strong> Anything else — content ideas, audience feedback, things to try next week.</li>
    </ul>

    <p>Just write it naturally — I'll parse it and update the pipeline's memory.</p>
    """

    send_draft_email(
        subject=f"[WEEKLY REVIEW] Performance check-in — {datetime.now(timezone.utc).strftime('%B %d, %Y')}",
        html_body=html,
    )
    logger.info("Weekly prompt email sent")


def parse_and_update(notes: str):
    """Parse free-form performance notes and update state.json."""
    state = load_state()
    pending = [p for p in state.get("performance", []) if p.get("score") == "pending"]

    prompt = f"""You're analyzing weekly social media performance notes to update a content pipeline's memory.

PERFORMANCE NOTES FROM THE USER:
{notes}

POSTS THAT WERE PENDING REVIEW:
{[{"id": p["id"], "platform": p["platform"], "hook": p["hook"], "format": p["format"], "topic": p["topic"]} for p in pending[-20:]]}

Based on the notes, generate updates:

Return JSON:
{{
  "post_updates": [
    {{
      "id": "<post_id if identifiable, or 'unknown'>",
      "score": "high" | "medium" | "low",
      "likes": <int or 0>,
      "saves": <int or 0>,
      "comments": <int or 0>,
      "impressions": <int or 0>
    }}
  ],
  "hook_patterns": {{
    "high": ["<hooks/patterns that worked well>"],
    "medium": ["<hooks/patterns that did okay>"],
    "low": ["<hooks/patterns that flopped>"]
  }},
  "top_formats": ["<formats that performed best>"],
  "top_topics": ["<topics that performed best>"],
  "weekly_learnings": "<2-3 sentence summary of what to carry forward into next week's content generation>"
}}
"""

    result = generate_json(prompt, system_instruction="You are analyzing social media performance data. Be precise and actionable.")

    # Apply post updates
    perf_by_id = {p["id"]: p for p in state["performance"]}
    for update in result.get("post_updates", []):
        pid = update.get("id")
        if pid in perf_by_id:
            perf_by_id[pid]["score"] = update.get("score", "pending")
            perf_by_id[pid]["likes"] = update.get("likes", 0)
            perf_by_id[pid]["saves"] = update.get("saves", 0)
            perf_by_id[pid]["comments"] = update.get("comments", 0)
            perf_by_id[pid]["impressions"] = update.get("impressions", 0)

    # Merge hook patterns (append, don't replace)
    for tier in ["high", "medium", "low"]:
        existing = state["hook_patterns"].get(tier, [])
        new = result.get("hook_patterns", {}).get(tier, [])
        state["hook_patterns"][tier] = list(set(existing + new))

    # Update top formats and topics
    if result.get("top_formats"):
        state["top_formats"] = result["top_formats"]
    if result.get("top_topics"):
        state["top_topics"] = result["top_topics"]

    # Update weekly learnings
    state["weekly_learnings"] = result.get("weekly_learnings", state.get("weekly_learnings", ""))

    save_state(state)
    logger.info("State updated with performance data")
    logger.info(f"Weekly learnings: {state['weekly_learnings']}")


def main():
    parser = argparse.ArgumentParser(description="Weekly Performance Updater")
    parser.add_argument("--prompt", action="store_true", help="Send the weekly check-in email")
    parser.add_argument("--update", type=str, help="Performance notes as a string")
    parser.add_argument("--update-file", type=str, help="Path to a text file with performance notes")
    args = parser.parse_args()

    if args.prompt:
        send_prompt_email()
    elif args.update:
        parse_and_update(args.update)
    elif args.update_file:
        with open(args.update_file, "r") as f:
            parse_and_update(f.read())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
