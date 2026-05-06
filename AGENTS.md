# bmo-persona Agent Notes

- Keep the repo focused on BMO-specific extraction, examples, and evaluation.
- Keep the full transcript archive in `data/raw/adventure-time-transcripts/`, one file per episode, so extraction can run locally without fetching live pages.
- Prefer deterministic parsing from captured transcript pages over invented dialogue.
- When scripts change, regenerate the derived files in `data/`.
- Treat `data/raw/adventure-time-transcripts/` as the source-of-truth episode archive for reruns.
