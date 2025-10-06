# Content Transformation (Finite State Transducers) — Step 3

- Replace flagged words with `***`.
- Produce suggestions (warnings) when hate/offensive/spam is detected.

Run:
```bash
python -m moderation.content_transformation_fst "You are stupid! visit http://a.com #wow"
```
