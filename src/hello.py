"""Smoke test: say hello to every configured model and print timings."""

from llm import LLMError, MODEL_ENV_VARS, call

PROMPT = "Say hello in five words"


def _fmt(value, unit="", digits=2):
    return "n/a" if value is None else f"{value:.{digits}f}{unit}"


def main():
    for model_name in MODEL_ENV_VARS:
        print(f"=== {model_name} ===")
        try:
            result = call(model_name, PROMPT)
        except LLMError as e:
            print(f"ERROR: {e}\n")
            continue

        print(f"model_id:      {result['model_id']}")
        print(f"reply:         {result['text'].strip()}")
        if result["reasoning"]:
            print(f"reasoning:     {len(result['reasoning'])} chars")
        print(f"ttft:          {_fmt(result['ttft_seconds'], 's')}")
        print(f"total:         {_fmt(result['total_seconds'], 's')}")
        print(f"output_tokens: {result['output_tokens'] if result['output_tokens'] is not None else 'n/a'}")
        print(f"tokens/sec:    {_fmt(result['tokens_per_second'], digits=1)}")
        print()


if __name__ == "__main__":
    main()
