# Voyager: An Open-Ended Embodied Agent with Large Language Models (arxiv:2305.16291)

> Authors: Wang et al. | Year: 2023 (NeurIPS 2023)

## Core Problem
Enable LLM-driven agents to autonomously explore, acquire skills, and make continual progress in open-ended environments without human intervention.

## Method Architecture
- **Automatic Curriculum**: Dynamically adjusts task difficulty based on agent's current skill level, driven by "discover new things" without human reward functions
- **Skill Library**: Code-as-Skill — each successful execution generates executable code stored in a library, retrieved via semantic embeddings (text-embedding-ada-002)
- **Iterative Prompting**: Automatic reflection and refinement on failure, self-correcting before retry

## Key Contributions
- Open-ended skill discovery paradigm combining curriculum learning + skill library + iterative prompting
- Semantic embedding retrieval for relevant skill selection
- No human reward engineering required

## Limitations
Not explicitly stated in notes.

## Optics_agent Lessons
- Code-as-Skill + Skill Library paradigm directly maps to COMSOL Java code as skill carrier
- Each successful simulation script can be auto-archived into the skill library
- Automatic curriculum maps to "increasing complexity" — simple geometry → multiphysics coupling → full parameter sweep
- Semantic retrieval of past COMSOL scripts based on physics configuration
