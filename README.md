# bmo-persona

Dedicated persona repo for BMO.

This repo is the home for a standalone BMO persona. Prior art lives in `bmo` and `bmo-embedded`; this repo should focus on the persona prompt, examples, and any Zo-specific delivery notes.
Transcript source copies live in `data/raw/` so extraction can rerun locally without fetching live pages.

## Scope

- BMO voice prompt
- BMO-specific examples and counterexamples
- Lightweight guidance for playful, friendly interactions
- Links back to the Adventure Time prior art

## Current status

Seeded with local transcript copies and a first pass of extracted examples. Next step is to refine the prompt and source mix.

## Extraction

Capture the transcript pages into `data/raw/`, then run:

```bash
python -m scripts.extract_bmo_persona
```

Outputs:

- `data/bmo_examples.jsonl`
- `data/bmo_train.jsonl`
- `data/bmo_eval.jsonl`
- `data/bmo_counterexamples.jsonl`
- `data/bmo_extract_report.md`
