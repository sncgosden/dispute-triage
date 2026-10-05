# Run configuration

## Claude API pricing used for cost figures

- Model: `claude-sonnet-5-5` (Claude Sonnet 5.5)
- Price: **$2 per million input tokens, $10 per million output tokens** (standard, non-batch)
- Source: Anthropic pricing page, https://platform.claude.com/docs/en/about-claude/pricing
- Checked: 5 October 2026
- Not used: Batch API (50% off, but results arrive asynchronously) and prompt caching (cache reads at 10% of the input price). Both could cut cost in production; see the decision memo.

Scoring command: `python src/score.py <results.jsonl> --price-in 2 --price-out 10`
