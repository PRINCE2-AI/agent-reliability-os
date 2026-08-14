from __future__ import annotations


MODEL_PRICES_PER_1K = {
    "openrouter/free": (0.0, 0.0),
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4.1-mini": (0.0004, 0.0016),
}


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))


def estimate_cost(model: str, input_text: str, output_text: str) -> float:
    input_price, output_price = MODEL_PRICES_PER_1K.get(model, (0.0004, 0.0016))
    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)
    return round((input_tokens / 1000) * input_price + (output_tokens / 1000) * output_price, 6)

