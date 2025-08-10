def calculate_cost(prompt_tokens: int, output_tokens: int) -> float:
    # Using specific pricing for Gemini 1.5 Flash
    if prompt_tokens <= 128000:
        input_cost_per_million = 0.075
        output_cost_per_million = 0.30
    else:
        input_cost_per_million = 0.15
        output_cost_per_million = 0.60

    input_cost = (prompt_tokens / 1_000_000) * input_cost_per_million
    output_cost = (output_tokens / 1_000_000) * output_cost_per_million

    return round(input_cost + output_cost, 6)