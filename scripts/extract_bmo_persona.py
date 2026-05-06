#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from bs4 import BeautifulSoup


REPO_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = REPO_DIR / "data" / "raw" / "adventure-time-transcripts"
OUTPUT_DIR = REPO_DIR / "data"
OUTPUT_EXAMPLES = OUTPUT_DIR / "bmo_examples.jsonl"
OUTPUT_TRAIN = OUTPUT_DIR / "bmo_train.jsonl"
OUTPUT_EVAL = OUTPUT_DIR / "bmo_eval.jsonl"
OUTPUT_COUNTEREXAMPLES = OUTPUT_DIR / "bmo_counterexamples.jsonl"
OUTPUT_REPORT = OUTPUT_DIR / "bmo_extract_report.md"

PERSONA_SYSTEM = (
    "Respond as BMO from Adventure Time. "
    "Be playful, friendly, and lightly mischievous. "
    "Use simple language and short bursts of energy. "
    "Keep the tone warm without becoming generic or syrupy."
)

SPEAKER_RE = re.compile(
    r"^([A-Z][A-Za-z0-9 '().\-\/]+?)(?:\s*\[(?P<bracket>[^\]]+)\])?\s*:\s*(?P<text>.+)$"
)
MARKDOWN_SPEAKER_RE = re.compile(
    r"^(?:[:\-]\s*)?\*\*(?P<speaker>[^*\[]+?)(?:\s*\[(?P<bracket>[^\]]+)\])?\*\*\s*:\s*(?P<text>.+)$"
)
LEADING_STAGE_RE = re.compile(r"^\[(?P<stage>[^\]]+)\]\s*(?P<text>.*)$")
HTML_NOISE_RE = re.compile(r"\[(?:edit|citation needed|source|music|laughs?)\]", re.IGNORECASE)


def stable_id(*parts: object) -> str:
    payload = "|".join(str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")
    if path.suffix.lower() in {".html", ".htm"}:
        soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        content = soup.select_one(".mw-parser-output") or soup.body or soup
        transcript_head = content.find("span", id="Transcript")
        if transcript_head and transcript_head.parent:
            transcript_lines: list[str] = []
            for sibling in transcript_head.parent.next_siblings:
                if getattr(sibling, "name", None) == "h2":
                    break
                if getattr(sibling, "name", None) != "dl":
                    continue
                for dd in sibling.find_all("dd", recursive=False):
                    text = re.sub(r"\s+", " ", dd.get_text(" ", strip=True)).strip()
                    if text:
                        transcript_lines.append(text)
            if transcript_lines:
                return "\n".join(transcript_lines)
        return content.get_text("\n")
    return path.read_text(encoding="utf-8", errors="replace")


def normalize(text: str) -> str:
    text = HTML_NOISE_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_blocks(text: str, source_name: str) -> list[dict]:
    blocks: list[dict] = []
    for line_num, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        md_match = MARKDOWN_SPEAKER_RE.match(stripped)
        if md_match:
            speaker = normalize(md_match.group("speaker"))
            stage = md_match.group("bracket") or ""
            text_value = normalize(md_match.group("text"))
            if not text_value:
                leading_stage = LEADING_STAGE_RE.match(md_match.group("text"))
                if leading_stage:
                    stage = normalize(f"{stage} {leading_stage.group('stage')}")
                    text_value = normalize(leading_stage.group("text"))
            blocks.append(
                {
                    "source": source_name,
                    "line_num": line_num,
                    "speaker": speaker,
                    "stage": stage,
                    "text": text_value,
                }
            )
            continue
        match = SPEAKER_RE.match(stripped)
        if not match:
            continue

        speaker = normalize(match.group(1))
        stage = match.group("bracket") or ""
        text_value = normalize(match.group("text"))
        if not text_value:
            leading_stage = LEADING_STAGE_RE.match(match.group("text"))
            if leading_stage:
                stage = normalize(f"{stage} {leading_stage.group('stage')}")
                text_value = normalize(leading_stage.group("text"))
        blocks.append(
            {
                "source": source_name,
                "line_num": line_num,
                "speaker": speaker,
                "stage": stage,
                "text": text_value,
            }
        )
    return blocks


def is_bmo_block(block: dict) -> bool:
    speaker = block["speaker"].upper()
    return speaker == "BMO" or speaker.startswith("BMO ")


def build_examples(blocks: list[dict], context_lines: int, eval_every: int) -> tuple[list[dict], list[dict], list[dict], dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for block in blocks:
        grouped[block["source"]].append(block)

    examples: list[dict] = []
    train_rows: list[dict] = []
    eval_rows: list[dict] = []
    counterexamples: list[dict] = []
    bmo_count = 0

    for source_name, rows in grouped.items():
        for index, block in enumerate(rows):
            if not is_bmo_block(block):
                continue

            bmo_count += 1
            context: list[dict] = []
            cursor = index - 1
            while cursor >= 0 and len(context) < context_lines:
                candidate = rows[cursor]
                if is_bmo_block(candidate):
                    cursor -= 1
                    continue
                context.append(candidate)
                cursor -= 1

            context.reverse()
            context_text = "\n".join(f"{item['speaker']}: {item['text']}" for item in context)
            record = {
                "id": stable_id(source_name, block["line_num"], block["text"]),
                "messages": [
                    {"role": "system", "content": PERSONA_SYSTEM},
                    {"role": "user", "content": context_text or "Okay!"},
                    {"role": "assistant", "content": block["text"]},
                ],
                "metadata": {
                    "speaker": "BMO",
                    "source_file": source_name,
                    "line_num": block["line_num"],
                    "stage": block["stage"],
                },
            }
            examples.append(record)
            target = eval_rows if eval_every > 0 and bmo_count % eval_every == 0 else train_rows
            target.append(record)

            for item in context:
                counterexamples.append(
                    {
                        "id": stable_id("counter", source_name, block["line_num"], item["line_num"], item["speaker"], item["text"]),
                        "speaker": item["speaker"],
                        "source_file": source_name,
                        "line_num": item["line_num"],
                        "text": item["text"],
                        "context": context_text,
                        "reason": "near-miss line from surrounding BMO context",
                    }
                )

    summary = {
        "source_blocks": len(blocks),
        "bmo_blocks": bmo_count,
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "counterexamples": len(counterexamples),
    }
    return examples, train_rows, eval_rows, counterexamples, summary


def build_report(examples: list[dict], counterexamples: list[dict], summary: dict) -> str:
    from collections import Counter

    source_mix = Counter(row["metadata"]["source_file"] for row in examples)
    samples = [row["messages"][2]["content"] for row in examples[:5]]
    return "\n".join(
        [
            "# BMO Persona Extract Report",
            "",
            f"- Source directory: `{DEFAULT_SOURCE_DIR}`",
            f"- Parsed transcript blocks: {summary['source_blocks']}",
            f"- Extracted BMO examples: {summary['train_rows'] + summary['eval_rows']}",
            f"- Counterexamples: {summary['counterexamples']}",
            "",
            "## Source mix",
            "",
            "| Source file | Count |",
            "|---|---:|",
            *[f"| {source} | {count} |" for source, count in sorted(source_mix.items())],
            "",
            "## Sample assistant lines",
            "",
            *[f"- {line}" for line in samples],
            "",
            "## Notes",
            "",
            "- The extractor only keeps dialogue lines that match transcript speaker labels.",
            "- Sync `data/raw/adventure-time-transcripts/` with `scripts/sync_adventure_time_transcripts.py`, then rerun this script.",
        ]
    )


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
        + ("\n" if rows else ""),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a BMO persona corpus from transcript pages in data/raw.")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR, help="Directory containing captured transcript HTML or text files.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Directory for the generated BMO persona artifacts.")
    parser.add_argument("--context-lines", type=int, default=2, help="Number of preceding non-BMO lines to include as prompt context.")
    parser.add_argument("--eval-every", type=int, default=6, help="Put every Nth BMO example into the eval split.")
    args = parser.parse_args()

    source_files = sorted(
        [
            path
    for path in args.source_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".html", ".htm", ".txt", ".md"}
        ]
    )
    if not source_files:
        raise FileNotFoundError(f"No transcript files found in {args.source_dir}")

    blocks: list[dict] = []
    for path in source_files:
        text = read_text(path)
        blocks.extend(parse_blocks(text, str(path.relative_to(args.source_dir))))

    examples, train_rows, eval_rows, counterexamples, summary = build_examples(
        blocks,
        context_lines=args.context_lines,
        eval_every=args.eval_every,
    )

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "bmo_examples.jsonl", examples)
    write_jsonl(output_dir / "bmo_train.jsonl", train_rows)
    write_jsonl(output_dir / "bmo_eval.jsonl", eval_rows)
    write_jsonl(output_dir / "bmo_counterexamples.jsonl", counterexamples)
    (output_dir / "bmo_extract_report.md").write_text(
        build_report(examples, counterexamples, summary) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {output_dir / 'bmo_examples.jsonl'}")
    print(f"Wrote {output_dir / 'bmo_train.jsonl'}")
    print(f"Wrote {output_dir / 'bmo_eval.jsonl'}")
    print(f"Wrote {output_dir / 'bmo_counterexamples.jsonl'}")
    print(f"Wrote {output_dir / 'bmo_extract_report.md'}")


if __name__ == "__main__":
    main()
