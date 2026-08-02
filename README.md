# German Sentence a Day (A2 / low B1)

A self-hosted RSS feed that publishes one German sentence a day, with an
English translation, level, and grammar tag. Fully automated via GitHub
Actions + GitHub Pages — free, no server, no API keys.

## How it works

- `sentences.json` — the sentence bank (72 to start). Add more any time by
  editing this file in the GitHub web UI; no coding needed. Just keep the
  same `id`/`de`/`en`/`level`/`grammar` fields and give each new entry a
  unique `id`.
- `generate_feed.py` — picks the next sentence in order each day, logs it in
  `history.json` (so re-runs don't duplicate), and rebuilds `rss.xml` from
  the most recent 30 days.
- `.github/workflows/daily.yml` — runs the script every day at 06:00 UTC and
  commits the updated feed. You can also trigger it manually from the
  Actions tab.

## Setup (one-time, ~10 minutes)

1. **Create a new GitHub repo** (public), e.g. `german-sentence-feed`.
2. **Upload these files** to the repo — either drag-and-drop via the GitHub
   web UI, or:
   ```
   git init
   git remote add origin https://github.com/YOUR_USERNAME/german-sentence-feed.git
   git add .
   git commit -m "Initial setup"
   git branch -M main
   git push -u origin main
   ```
3. **Edit `generate_feed.py`**: replace `YOUR_USERNAME` in `FEED_LINK` and
   `FEED_SELF_URL` with your actual GitHub username (or custom domain if you
   set one up). Commit the change.
4. **Enable GitHub Pages**: repo → Settings → Pages → under "Build and
   deployment", set Source to "Deploy from a branch", branch `main`, folder
   `/ (root)`. Save.
5. **Run the workflow once manually**: repo → Actions tab → "Update German
   sentence feed" → "Run workflow". This generates the first `rss.xml` and
   `history.json` and commits them.
6. Wait a minute or two, then check your feed is live at:
   ```
   https://YOUR_USERNAME.github.io/german-sentence-feed/rss.xml
   ```
7. **Subscribe** to that URL in your RSS reader. From then on, it updates
   itself every day automatically.

## Customising

- **Change the schedule**: edit the `cron` line in
  `.github/workflows/daily.yml` (it's in UTC).
- **Change how many items appear in the feed**: edit `MAX_FEED_ITEMS` in
  `generate_feed.py`.
- **Reorder or reshuffle sentences**: the script publishes sentences in the
  order they appear in `sentences.json`, cycling back to the start once
  exhausted. Reorder the array to change the sequence, or add a shuffle step
  if you'd rather it be random.
- **Add audio/pronunciation later**: you could extend each sentence entry
  with an audio URL (e.g. from a TTS service) and reference it as an
  enclosure in the RSS item — not included here to keep the initial setup
  simple.
