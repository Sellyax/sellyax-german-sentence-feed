#!/usr/bin/env python3
"""
Generates a daily kettlebell movement RSS feed. Same pattern as
generate_feed.py, kept as a separate script so the two feeds are
completely independent (separate bank, history, and output file).
"""
import json
import os
from datetime import date, datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVEMENTS_PATH = os.path.join(BASE_DIR, "kettlebell.json")
HISTORY_PATH = os.path.join(BASE_DIR, "kettlebell_history.json")
FEED_PATH = os.path.join(BASE_DIR, "kettlebell.xml")

FEED_TITLE = "Kettlebell Movement a Day"
FEED_DESCRIPTION = "One kettlebell movement a day with a short coaching cue."
FEED_LINK = "https://Sellyax.github.io/sellyax-german-sentence-feed/"
FEED_SELF_URL = "https://Sellyax.github.io/sellyax-german-sentence-feed/kettlebell.xml"

MAX_FEED_ITEMS = 30


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_history(movements, history):
    today = date.today().isoformat()
    if any(entry["date"] == today for entry in history):
        return history

    next_index = len(history) % len(movements)
    movement = movements[next_index]
    history.append({"date": today, "movement_id": movement["id"]})
    return history


def build_rss(movements, history):
    by_id = {m["id"]: m for m in movements}
    recent = history[-MAX_FEED_ITEMS:][::-1]

    items_xml = []
    for entry in recent:
        movement = by_id.get(entry["movement_id"])
        if not movement:
            continue
        pub_dt = datetime.fromisoformat(entry["date"]).replace(
            hour=6, minute=10, tzinfo=timezone.utc
        )
        title = escape(movement["movement"])
        description_html = (
            f'{movement["cue"]}<br><br>'
            f'Category: {movement["category"]} &nbsp;|&nbsp; Level: {movement["level"]}'
        )
        guid = f'{entry["date"]}-{movement["id"]}'
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
    <language>en</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{escape(FEED_SELF_URL)}" rel="self" type="application/rss+xml" />
{items_block}
  </channel>
</rss>
"""
    return rss


def main():
    movements = load_json(MOVEMENTS_PATH, [])
    if not movements:
        raise SystemExit("kettlebell.json is empty or missing.")

    history = load_json(HISTORY_PATH, [])
    history = update_history(movements, history)
    save_json(HISTORY_PATH, history)

    rss = build_rss(movements, history)
    with open(FEED_PATH, "w", encoding="utf-8") as f:
        f.write(rss)

    print(f"Kettlebell feed updated. {len(history)} movement(s) published so far.")


if __name__ == "__main__":
    main()
