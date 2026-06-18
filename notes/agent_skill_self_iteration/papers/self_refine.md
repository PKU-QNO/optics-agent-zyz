# Self-Refine: Iterative Refinement with Self-Feedback (arxiv:2303.17651)

> Authors: Madaan et al. | Year: 2023

## Core Problem
A single LLM can iteratively improve its own output without external supervision or fine-tuning.

## Method Architecture
- **Generator**: Produces initial output
- **Feedback**: Same LLM evaluates its own output, providing自然语言 feedback
- **Refiner**: Same LLM revises output based on feedback
- All three roles played by the same LLM in sequence

## Key Contributions
- ~20% average improvement across 7 diverse tasks
- No external supervision, no fine-tuning, no additional models required
- Established self-feedback as a foundational paradigm for LLM self-improvement

## Limitations
- Self-Bias discovered in subsequent work (2402.11436) — self-feedback alone leads to recursive drift
- Larger models and external feedback can mitigate self-bias

## Optics_agent Lessons
- Paper reproduction report generation → agent auto-review → self-correct from numerical plausibility perspective
- Three-stage pattern (generate → feedback → refine) maps to simulation pipeline audit
- External validator/critic is essential — do not rely solely on self-feedback for scientific correctness
