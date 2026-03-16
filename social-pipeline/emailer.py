"""Send draft posts via Gmail SMTP using App Passwords."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, DRAFT_RECIPIENT

logger = logging.getLogger(__name__)


def send_draft_email(subject: str, html_body: str) -> bool:
    """Send an HTML email via Gmail SMTP.

    Requires a Gmail App Password (not regular password).
    Generate one at: https://myaccount.google.com/apppasswords
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        logger.error("Gmail credentials not configured. Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = DRAFT_RECIPIENT
    msg["Subject"] = subject

    # Plain text fallback
    plain = html_body.replace("<br>", "\n").replace("<hr>", "\n---\n")
    # Strip remaining tags for plain text
    import re
    plain = re.sub(r"<[^>]+>", "", plain)

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def format_breaking_news_email(story: dict, twitter_post: str, ig_caption: str, image_concept: str) -> str:
    """Format a breaking news draft into HTML."""
    return f"""
    <h2>🚨 Breaking AI News</h2>
    <p><strong>Story:</strong> {story.get('title', 'Untitled')}</p>
    <p><strong>Source:</strong> <a href="{story.get('link', '#')}">{story.get('source', 'Unknown')}</a></p>
    <p><strong>Score:</strong> {story.get('score', 'N/A')}/10</p>
    <hr>
    <h3>Twitter/X Post</h3>
    <div style="background: #f5f5f5; padding: 12px; border-radius: 8px; font-family: sans-serif;">
        {twitter_post}
    </div>
    <p><em>({len(twitter_post)} chars)</em></p>
    <hr>
    <h3>Instagram Caption</h3>
    <div style="background: #f5f5f5; padding: 12px; border-radius: 8px; font-family: sans-serif;">
        {ig_caption.replace(chr(10), '<br>')}
    </div>
    <hr>
    <h3>Image Concept</h3>
    <p>{image_concept}</p>
    """


def format_daily_digest_email(posts: list[dict]) -> str:
    """Format multiple daily content pieces into a single HTML digest."""
    sections = []
    for i, post in enumerate(posts, 1):
        sections.append(f"""
        <h3>Post {i}: {post.get('format', 'Unknown format')}</h3>
        <p><strong>Topic:</strong> {post.get('topic', '')}</p>
        <p><strong>Hook:</strong> {post.get('hook', '')}</p>
        <hr>
        <h4>Instagram Caption</h4>
        <div style="background: #f5f5f5; padding: 12px; border-radius: 8px;">
            {post.get('ig_caption', '').replace(chr(10), '<br>')}
        </div>
        <h4>Twitter/X Post</h4>
        <div style="background: #f5f5f5; padding: 12px; border-radius: 8px;">
            {post.get('twitter_post', '')}
        </div>
        <p><em>({len(post.get('twitter_post', ''))} chars)</em></p>
        <h4>Image Concept</h4>
        <p>{post.get('image_concept', '')}</p>
        <hr style="border: 2px solid #333;">
        """)
    return f"""
    <h2>📋 Daily Content Digest</h2>
    <p>3 posts ready for review and publishing.</p>
    {''.join(sections)}
    """
