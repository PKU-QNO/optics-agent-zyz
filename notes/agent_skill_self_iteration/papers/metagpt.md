# MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework (arxiv:2308.00352)

> Authors: Hong et al. | Year: 2023

## Core Problem
Complex software engineering requires specialized role分工, but existing single-agent systems lack structured collaboration and SOP-driven workflows.

## Method Architecture
- **SOP Pipeline**: Code(Team) = SOP-driven multi-agent collaboration
- **Role Division**: PM, Architect, Engineer, Tester — each with defined responsibilities and outputs
- **AFlow**: Automated workflow generation (ICLR 2025 Oral)

## Key Contributions
- 68.9k stars — widely adopted multi-agent framework
- "Software company metaphor" as天然 role-skill separation framework
- Demonstrates that role specialization outperforms monolithic agents on complex tasks
- SOP = structured流程 for reproducible multi-agent collaboration

## Limitations
- Role structure fixed after definition, making extension costly
- Flexibility limited compared to Tool-as-Skill architectures

## Optics_agent Lessons
- COMSOL simulation SOP maps directly to role pipeline: paper reader → model builder → solver → post-processor → report generator
- Role specialization for complex scientific computing workflows
- Medium-term目标:引入角色Agent模板 (paper-reader, model-builder, magnus-submitter, result-validator)
