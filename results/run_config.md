# Run configuration

## Claude API pricing used for cost figures

- Model: `claude-sonnet-5-5` (Claude Sonnet 5.5)
- Price: **$2 per million input tokens, $10 per million output tokens** (standard, non-batch)
- Source: Anthropic pricing page, https://platform.claude.com/docs/en/about-claude/pricing
- Checked: 5 October 2026
- Not used: Batch API (50% off, but results arrive asynchronously) and prompt caching (cache reads at 10% of the input price). Both could cut cost in production; see the decision memo.

Scoring command: `python src/score.py <results.jsonl> --price-in 2 --price-out 10`

## Local models (LM Studio)

Fill in once before the Qwen runs. Each run also saves its own settings automatically to `results/<run>.meta.jsonl` (models loaded according to `lms ps`, LM Studio version, git commit, prompt version).

| Setting | Value | Where to find it |
|---|---|---|
| Hardware | MacBook Air M5, 24 GB | |
| macOS version | _fill in_ | Apple menu → About This Mac |
| LM Studio version | _fill in_ | `lms version` |
| Small model | `QWEN_SMALL` in `.env`: Qwen 3.5 4B, mlx-community, MLX 4-bit | `lms ps` while loaded |
| Large model | `QWEN_LARGE` in `.env`: Qwen 3.5 9B, mlx-community, MLX 4-bit | `lms ps` while loaded |
| Embedding model | `text-embedding-nomic-embed-text-v1.5` | `lms ps` |
| Context length | 8,192 tokens (`lms load <id> --context-length 8192`) | |
| Models loaded at once | one Qwen model plus the embedding model | `lms ps` |
| Thinking mode | off (empty think block prefilled; see `src/llm.py`) | |
| Max output tokens | 1,000 | `src/triage.py` |
| Temperature | **0 for Qwen 4B and 9B**, set in code (`TEMPERATURE` in `src/triage.py`), overriding LM Studio's setting. Claude: API default; the SDK in use doesn't accept a temperature for this model. | |
| GPU offload | MLX models run fully on the Apple GPU (default) | |
| Power | plugged in, Low Power Mode off | System Settings → Battery |
| Other apps | heavy apps closed (browser tabs, video calls, Docker) | |

## Known limitations of the setup

- **Temperature differs between providers.** The Qwen models run at 0 (close to repeatable, though not guaranteed identical on GPU). Claude runs at its API default, because temperature can't be set for this model with the SDK in use. So Claude's results may vary slightly between runs. Re-running a sample would show by how much.
- **Timing includes retrieval** (local embedding call, typically well under 0.5s). It's reported separately as `retrieval_seconds`.
