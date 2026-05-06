#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import html
import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


REPO_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = REPO_DIR / "data" / "raw" / "adventure-time-transcripts"
API_URL = "https://adventuretime.fandom.com/api.php"


@dataclass(frozen=True)
class TranscriptPage:
    pageid: int
    title: str
    filename: str
    url: str


def slugify(text: str) -> str:
    text = re.sub(r"/Transcript$", "", text, flags=re.IGNORECASE)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "transcript"


def fetch_json(params: dict[str, Any], retries: int = 3, pause: float = 1.0) -> dict[str, Any]:
    query = urlencode(params)
    url = f"{API_URL}?{query}"
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = Request(url, headers={"User-Agent": "bmo-persona-sync/1.0"})
            with urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(pause * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}") from last_error


def list_transcript_pages() -> list[TranscriptPage]:
    pages: list[TranscriptPage] = []
    cont: str | None = None
    while True:
        params: dict[str, Any] = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Category:Transcripts",
            "cmlimit": "max",
            "format": "json",
        }
        if cont:
            params["cmcontinue"] = cont
        payload = fetch_json(params)
        for item in payload.get("query", {}).get("categorymembers", []):
            title = str(item["title"])
            if not title.endswith("/Transcript"):
                continue
            pageid = int(item["pageid"])
            stem = f"{pageid}-{slugify(title)}"
            pages.append(
                TranscriptPage(
                    pageid=pageid,
                    title=title,
                    filename=f"{stem}.html",
                    url=f"https://adventuretime.fandom.com/wiki/{quote(title.replace(' ', '_'), safe='')}",
                )
            )
        cont = payload.get("continue", {}).get("cmcontinue")
        if not cont:
            break
    return pages


def fetch_rendered_html(pageid: int) -> str:
    payload = fetch_json(
        {
            "action": "parse",
            "pageid": pageid,
            "prop": "text",
            "format": "json",
            "formatversion": 2,
        }
    )
    return str(payload["parse"]["text"])


def wrap_html(title: str, body: str) -> str:
    return "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"en\">",
                "<head>",
                '  <meta charset="utf-8" />',
                f"  <title>{html.escape(title)}</title>",
                "</head>",
            "<body>",
            body,
            "</body>",
            "</html>",
        ]
    )


def sync_one(page: TranscriptPage, source_dir: Path, refresh: bool) -> TranscriptPage:
    out = source_dir / page.filename
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not refresh:
        return page
    html = fetch_rendered_html(page.pageid)
    out.write_text(wrap_html(page.title, html) + "\n", encoding="utf-8")
    return page


def main() -> None:
    parser = argparse.ArgumentParser(description="Mirror Adventure Time transcript pages into data/raw/adventure-time-transcripts.")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR, help="Directory to write transcript HTML files.")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent page fetches.")
    parser.add_argument("--refresh", action="store_true", help="Re-download pages even if they already exist.")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of transcript pages synced.")
    args = parser.parse_args()

    pages = list_transcript_pages()
    if args.limit > 0:
        pages = pages[: args.limit]

    args.source_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.source_dir / "_manifest.json"

    results: list[TranscriptPage] = []
    failures: list[str] = []
    with cf.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(sync_one, page, args.source_dir, args.refresh): page for page in pages}
        for index, future in enumerate(cf.as_completed(futures), start=1):
            page = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{page.title}: {exc}")
            if index % 25 == 0 or index == len(futures):
                print(f"[{index}/{len(futures)}] synced")

    manifest_path.write_text(
        json.dumps([asdict(page) for page in sorted(results, key=lambda item: item.pageid)], indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(results)} transcript files to {args.source_dir}")
    print(f"Wrote manifest to {manifest_path}")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
