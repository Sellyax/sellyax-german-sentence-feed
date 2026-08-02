#!/usr/bin/env python3
"""
Generates a daily German sentence RSS feed.

- Reads sentences.json (the sentence bank).
- Reads/updates history.json (log of which sentence was published on which day).
- Cycles through the bank in order, one new sentence per day. Re-running on the
  same day is safe (won't duplicate). Once the bank is exhausted it wraps back
  to the start.
- Rebuilds rss.xml from the most recent N entries in history.

Run this daily (e.g. via GitHub Actions). No external dependencies.
"""
import json
import os
from datetime import date, datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SENTENCES_PATH = os.path.join(BASE_DIR, "sentences.json")
HISTORY_PATH = os.path.join(BASE_DIR, "history.json")
FEED_PATH = os.path.join(BASE_DIR, "rss.xml")

# --- EDIT THESE to match your GitHub username/repo once you've created it ---
FEED_TITLE = "German Sentence a Day (A2 / low B1)"
FEED_DESCRIPTION = "One German sentence a day at A2 to low-B1 level, with an English translation and grammar tag."
FEED_LINK = "https://Sellyax.github.io/sellyax-german-sentence-feed/"
FEED_SELF_URL = "https://Sellyax.github.io/sellyax-german-sentence-feed/rss.xml"
# -----------------------------------------------------------------------------

MAX_FEED_ITEMS = 30


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_history(sentences, history):
    today = date.today().isoformat()
    if any(entry["date"] == today for entry in history):
        return history  # already published today, don't duplicate

    next_index = len(history) % len(sentences)
    sentence = sentences[next_index]
    history.append({"date": today, "sentence_id": sentence["id"]})
    return history


def build_rss(sentences, history):
    by_id = {s["id"]: s for s in sentences}
    recent = history[-MAX_FEED_ITEMS:][::-1]  # newest first

    items_xml = []
    for entry in recent:
        sentence = by_id.get(entry["sentence_id"])
        if not sentence:
            continue
        pub_dt = datetime.fromisoformat(entry["date"]).replace(
            hour=6, tzinfo=timezone.utc
        )
        title = escape(sentence["de"])
        description_html = (
            f'<details><summary>Show translation</summary><br><br><br><br>'
            f'{sentence["en"]}<br><br>'
            f'Level: {sentence["level"]} &nbsp;|&nbsp; Grammar: {sentence["grammar"]}'
            f'</details>'
        )
        guid = f'{entry["date"]}-{sentence["id"]}'
        items_xml.append(f"""    <item>
      <title>{title}</title>
      <description><![CDATA[{description_html}]]></description>
      <pubDate>{format_datetime(pub_dt)}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
    </item>""")
    now = format_datetime(datetime.now(timezone.utc))
    items_block = "\n".join(items_xml)

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(FEED_TITLE)}</title>
    <link>{escape(FEED_LINK)}</link>
    <description>{escape(FEED_DESCRIPTION)}</description>
    <language>de</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{escape(FEED_SELF_URL)}" rel="self" type="application/rss+xml" />
{items_block}
  </channel>
</rss>
"""
    return rss


def main():
    sentences = load_json(SENTENCES_PATH, [])
    if not sentences:
        raise SystemExit("sentences.json is empty or missing.")

    history = load_json(HISTORY_PATH, [])
    history = update_history(sentences, history)
    save_json(HISTORY_PATH, history)

    rss = build_rss(sentences, history)
    with open(FEED_PATH, "w", encoding="utf-8") as f:
        f.write(rss)

    print(f"Feed updated. {len(history)} sentence(s) published so far.")


if __name__ == "__main__":
    main()
