# Generative Agents: Interactive Simulacra of Human Behavior (arxiv:2304.03442)

> Authors: Park et al. | Year: 2023

## Core Problem
LLM-powered agents in interactive environments lack coherent long-term behavior, memory, and social interaction capabilities.

## Method Architecture
- **Memory Stream**: Streaming record of all experiences (timestamped, natural language)
- **Retrieval**: Relevance + recency + importance weighted scoring to surface relevant memories
- **Reflection**: High-level abstractions and insights synthesized from memory patterns
- **Planning**: Hierarchical plan decomposition based on retrieved memories and reflections

## Key Contributions
- 25 agents exhibit emergent social behaviors in Stanford小镇 simulation
- Demonstrates that memory architecture is key to coherent long-term agent behavior
- Retrieval weighting (relevance + time + importance) provides effective memory recall

## Limitations
Not explicitly stated in notes.

## Optics_agent Lessons
- Multi-agent role design (modeler/solver/analyst) can借鉴 this architecture
- Memory stream for tracking COMSOL simulation history across sessions
- Reflection component for synthesizing high-level failure patterns from low-level simulation logs
- Planning component for hierarchical decomposition of complex reproduction workflows
- Retrieval weighting applicable to experience pool query (relevance + recency + importance)
