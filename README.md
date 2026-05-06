# bmo-persona

Dedicated persona repo for BMO.

This repo is the home for a standalone BMO persona. Prior art lives in `bmo` and `bmo-embedded`; this repo should focus on the persona prompt, examples, and any Zo-specific delivery notes.
The full Adventure Time transcript archive lives in `data/raw/adventure-time-transcripts/`, one file per episode, so extraction can rerun locally without fetching live pages.

## Scope

- BMO voice prompt
- BMO-specific examples and counterexamples
- Lightweight guidance for playful, friendly interactions
- Links back to the Adventure Time prior art

## Current status

Seeded with a full transcript archive and a first pass of extracted examples. The next step is to keep the archive in sync, then rerun extraction so the corpus stays episode-based and reproducible.

## Extraction

Sync the transcript archive, then run:

```bash
python -m scripts.sync_adventure_time_transcripts
python -m scripts.extract_bmo_persona
```

Outputs:

- `data/bmo_examples.jsonl`
- `data/bmo_train.jsonl`
- `data/bmo_eval.jsonl`
- `data/bmo_counterexamples.jsonl`
- `data/bmo_extract_report.md`

## Source mix

The main corpus source set is the transcript archive in `data/raw/adventure-time-transcripts/`. Older handpicked captures remain in `data/raw/` for reference, but they are no longer the default extraction input.
