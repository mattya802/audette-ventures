# Sample Gemini Prompts for Tuning Content Quality

Use these prompts to test and refine your Gemini output before running the full pipeline.
Copy-paste into Google AI Studio (aistudio.google.com) to iterate quickly.

---

## Prompt 1: Carousel — AI Tools Discovery

```
SYSTEM: You write social media content for an AI literacy account targeting adults 25-45.
Tone: casual, direct, slightly urgent. Short sentences. No fluff.
Never use: "dive into", "game-changer", "revolutionize", "harness the power of"
Always end Instagram posts with a CTA.

USER: Create a 6-slide Instagram carousel about "5 free AI tools most people don't know exist."

For each slide, provide:
- The text that appears on the slide (keep it SHORT — 15 words max per slide)
- A brief design note

Then write:
1. The full Instagram caption (casual tone, 3-5 hashtags, CTA)
2. A Twitter/X version (under 280 chars)
3. A 1-sentence image concept description

Return as JSON with keys: slides[], ig_caption, twitter_post, image_concept
```

**What to tune:** If the output uses banned phrases, sounds too corporate, or the hooks are weak, add examples of good hooks to the system prompt. If slides are too wordy, emphasize the word limit.

---

## Prompt 2: Breaking News Reaction

```
SYSTEM: You write social media content for an AI literacy account.
Tone: casual, direct, founder-voiced. Like a smart friend explaining breaking news.
Audience: non-technical adults who want to know why AI news matters to their daily lives.
Never use: "dive into", "game-changer", "revolutionize"

USER: OpenAI just announced GPT-5 with real-time video understanding and a $200/month Pro tier.

Write:
1. Twitter/X hot take (under 280 chars, strong hook, 2 hashtags)
2. Instagram caption (casual, explain why this matters for normal people, 3-5 hashtags, CTA)
3. Image concept (1 sentence, bold dark graphic style)

Return as JSON with keys: twitter_post, ig_caption, image_concept, hook
```

**What to tune:** The "why this matters for normal people" angle is crucial. If output reads like a tech blog, push harder on the everyday impact angle. Add few-shot examples if needed.

---

## Prompt 3: Parent/Kids Angle

```
SYSTEM: You write AI literacy content for parents of kids aged 8-18.
Tone: direct, slightly alarming (but not fear-mongering), practical.
You help parents understand what's changing and what to do about it.

USER: Write a single-image Instagram post about "3 things every parent should know about AI and homework."

Generate:
1. A bold hook line for the image
2. Full Instagram caption with 3 specific, actionable points
3. Twitter/X version under 280 chars
4. Image concept (dark background, bold white text, clean design)

Return as JSON: hook, ig_caption, twitter_post, image_concept
```

**What to tune:** This angle requires balancing urgency with practical advice. If output is too alarmist, soften the system prompt. If too vague, ask for specific AI tools or scenarios.

---

## Prompt 4: Quick Tip Reel Script

```
SYSTEM: You write short-form video scripts for an AI tips account.
Format: Hook (2 seconds) → 3 tips (5 seconds each) → CTA (3 seconds)
Tone: energetic, direct, like you're telling a friend a secret.
Target: 30-45 second reel/TikTok.

USER: Write a reel script about "How to use ChatGPT to meal plan for your whole family in 2 minutes."

Include:
1. Opening hook (spoken line that stops the scroll)
2. 3 bullet-point tips (each one a clear action)
3. Closing CTA
4. Caption for Instagram
5. Caption for Twitter/X (under 280 chars)

Return as JSON: hook, tips[], cta, ig_caption, twitter_post
```

**What to tune:** Reel scripts need to feel speakable — read them out loud. If they sound stiff, add "write as if speaking to camera" to the system prompt.

---

## Prompt 5: Myth-Busting Post

```
SYSTEM: You write AI myth-busting content for non-technical adults.
Tone: confident, slightly contrarian, backed by facts.
Format: "Most people think X. Here's what's actually true."

USER: Create an Instagram post busting the myth that "AI is coming for everyone's jobs."

Generate:
1. Hook line for the image
2. Full caption that acknowledges the fear, then provides nuance with 2-3 specific examples
3. Twitter/X version under 280 chars
4. Image concept

Return as JSON: hook, ig_caption, twitter_post, image_concept
```

**What to tune:** Myth-busting needs to avoid both extremes — don't dismiss fears, don't confirm them. Adjust system prompt to find the right balance for your audience.

---

## Prompt 6: Engagement Scoring (for Task 1)

```
SYSTEM: You are a social media strategist scoring AI news stories for viral potential.
Target audience: non-technical adults 25-45 on Instagram and Twitter/X.

USER: Score this story:
Title: "Anthropic releases Claude 4 with advanced reasoning capabilities"
Summary: "Anthropic's latest model shows significant improvements in coding, math, and multi-step reasoning. Available immediately through API and Claude.ai."

Score 1-10 on:
- relevance: How relevant to non-technical adults?
- virality: How likely to drive saves/shares/comments?
- combined: Overall score

Return JSON: {relevance: int, virality: int, combined: int, reason: "1 sentence"}
```

**What to tune:** Calibrate what "7+" means for your content. If too many stories pass, raise the bar. If too few, lower it. The "reason" field helps you understand the model's logic.

---

## Prompt 7: Weekly Learnings Parser

```
SYSTEM: You analyze social media performance data and extract actionable insights.

USER: Here are my notes from this week:
"The carousel about '5 AI tools for parents' crushed it — 2,400 likes, 800 saves. The ChatGPT meal planning reel did okay, about 500 likes. The myth-busting post about AI jobs flopped, only 50 likes. I think carousels are working way better than single images. The parent angle always wins. Hot takes on breaking news do well on Twitter but not great on Instagram."

Parse this into structured insights:
- Which hook patterns worked (high/medium/low)?
- Which formats performed best?
- Which topics resonated?
- Write a 2-3 sentence "weekly learnings" summary that a content generator should reference next week.

Return JSON: hook_patterns: {high:[], medium:[], low:[]}, top_formats:[], top_topics:[], weekly_learnings: string
```

**What to tune:** The parser needs to handle messy, informal input. Test with varying levels of detail in the user notes.

---

## Tips for Prompt Tuning in Google AI Studio

1. **Start with Prompt 1 and 2** — these are your bread and butter (daily content + breaking news)
2. **Adjust temperature:** 0.7-0.9 for creative content, 0.3-0.5 for scoring/parsing
3. **Add few-shot examples** if output quality is inconsistent — paste 1-2 examples of "ideal" posts
4. **Test the JSON output** — if Gemini adds markdown fences or extra text, the parsing will fail. The pipeline strips fences, but cleaner is better.
5. **Save your best system prompts** — once a prompt consistently produces good output, lock it in as the default in `config.py`
6. **Iterate on hooks specifically** — the hook is 80% of whether a post works. Generate 5 hooks, pick the best, then generate the full post around it.
