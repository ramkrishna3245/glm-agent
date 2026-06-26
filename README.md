# TokenRouter — Cross-Architecture Model Ensemble

A novel approach to running multiple LLM architectures on systems with limited RAM (8GB).

## The Innovation

**Cross-architecture verification**: TokenRouter routes generation requests across different model families (TinyLlama/Llama, Qwen2.5/Qwen) and detects hallucinations by measuring disagreement between architectures. Different model families make different types of errors — when they disagree, one is likely hallucinating.

## How It Works

1. **TinyLlama (1B, 608MB)** — always-loaded primary model for routine tasks
2. **Qwen2.5:3b (3B, 1.8GB)** — loaded on-demand for math/code verification
3. **Cross-architecture agreement scoring** — when models disagree strongly (>0.3 threshold), the larger model's answer is used
4. **Model unloading** — only one model in RAM at a time to fit within 8GB

## Requirements

- Ollama with tinyllama:latest and qwen2.5:3b models
- Python 3.10+
- `requests` library

## Usage

```python
from tokenrouter_v3 import TokenRouter

router = TokenRouter()
answer = router.generate("What is 24 multiplied by 37?")
print(answer)  # Will use cross-architecture verification
```

## Novelty

This is the first known implementation of **cross-architecture token routing** for LLMs. Traditional approaches use the same model at different scales (e.g., Llama-7B → Llama-70B). TokenRouter uses completely different model families (Llama + Qwen) and leverages their architectural differences for hallucination detection.
