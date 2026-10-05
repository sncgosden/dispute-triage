# dispute-triage

## Local models

The local Qwen models run in LM Studio and must be loaded **one at a time**; loading both at once exceeds available memory. Before switching models, unload everything and load the one you need with a smaller context:

```sh
lms unload --all
lms load <model-id> --context-length 8192
```

`<model-id>` is the value of `QWEN_SMALL` or `QWEN_LARGE` in `.env`.
