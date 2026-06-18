# Reflexion: Language Agents with Verbal Reinforcement Learning (arxiv:2303.11366)

> Authors: Shinn et al. | Year: 2023 (NeurIPS 2023)

## Core Problem
Enable agents to learn from task failures through language feedback instead of expensive model weight updates.

## Method Architecture
- **Actor**: Generates actions/trajectories
- **Evaluator**: Assesses results and produces natural language feedback
- **Memory**: Three modes — short-term (current trajectory), long-term (cross-session experience), self-reflection (structured反思)

## Key Contributions
- Verbal reinforcement learning: natural language feedback replaces weight updates
- HumanEval 91% pass@1 — language feedback matches or exceeds RL performance
- Structured reflection stored in memory for future task guidance

## Limitations
Not explicitly stated in notes.

## Optics_agent Lessons
- Failed simulation scripts → language reflection → automatic workflow correction, no model retraining needed
- Can be directly applied to COMSOL failure diagnosis: matrix factorization failure triggers structured反思 for parameter tuning
- Runtime reflection (vs current post-hoc final_report.md approach)
- External validator/critic is essential — self-feedback alone leads to recursive drift
