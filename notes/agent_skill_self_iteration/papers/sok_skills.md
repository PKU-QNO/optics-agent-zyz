# SoK: Agentic Skills — Systematization of Knowledge (arxiv:2602.20867)

> Authors: Not specified in notes | Year: 2026

## Core Problem
Agent skill systems lack standardized design patterns, leading to ad-hoc implementations and incompatible architectures across frameworks.

## Method Architecture
Seven design patterns identified through systematic review:

1. **Metadata-driven Progressive Disclosure**: Load name+description first, full SKILL.md on demand
2. **Executable Code Skills**: Skill content includes directly executable code (e.g., COMSOL Java)
3. **Self-evolving Libraries**: Skills auto-evolve via trajectory distillation → task → self-evolution
4. **Marketplace Distribution**: Community marketplace分发 (tech-leads-club/agent-skills 4.6k⭐)
5. **Representation × Scope Taxonomy**: NL / Code / Policy / Hybrid四种表示
6. **Compositional Skill Synthesis**: Combine existing skills to create new capabilities
7. **Trust-tiered Execution**: Source-based security-level execution

## Key Contributions
- First systematic taxonomy of agent skill design patterns
- Enables structured comparison and evaluation across skill system implementations
- Provides vocabulary for describing skill architecture decisions

## Limitations
Not explicitly stated in notes.

## Optics_agent Lessons
- Seven patterns map directly to现有 8 skills refactoring
- Progressive disclosure already partially implemented (SKILL.md frontmatter)
- Self-evolving library is the key gap — enable skills to improve from execution history
- Executable code skills pattern aligns with COMSOL Java as skill载体
- Trust-tiered execution relevant for multi-source skill security
