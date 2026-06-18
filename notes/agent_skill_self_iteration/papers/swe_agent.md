# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering (arxiv:2405.15793)

> Authors: Yang et al. | Year: 2024

## Core Problem
LLM agents fail at software engineering tasks not because they lack capability, but because tool interfaces are not designed for agent consumption.

## Method Architecture
- **ACI (Agent-Computer Interface)**: Design tool interfaces to fit agent capabilities, not the reverse
- **Key Components**:
  - File Viewer: line-by-line with context window
  - Editor: replace-based (not append), precise surgical edits
  - Execution Shell: state-isolated command execution

## Key Contributions
- ACI paradigm shift — interface design matters more than model capability
- SWE-bench 12.5% pass@1 (SOTA at time of publication)
- Demonstration that tool design directly determines agent success rate

## Limitations
Not explicitly stated in notes.

## Optics_agent Lessons
- Magnus submission interface needs ACI redesign for agent consumption
- COMSOL CLI output parser must be adapted to agent's reading patterns
- File viewer/editor patterns for editing COMSOL Java files
- Framework design matters more than model — same model differs 6x across frameworks (Claw-SWE)
