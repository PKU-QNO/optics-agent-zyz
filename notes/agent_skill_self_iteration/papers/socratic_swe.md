# Socratic-SWE: Closed-loop Self-Evolving Code Agent (arxiv:2606.07412)

> Authors: Not specified in notes | Year: 2026

## Core Problem
Agent skills are static; they do not automatically improve from accumulated execution experience, limiting long-term autonomy.

## Method Architecture
- **Trajectory Distillation**: Extract structured agent skills from historical problem-solving trajectories
- **Guided Repair**: Distilled skills guide generation of targeted repair tasks
- **Execution-based Validation**: Repaired solutions are validated by execution
- **Solver Update**: Successful repairs update the skill library and solver

## Key Contributions
- SWE-bench Verified 50.40% after 3 iterations — significant improvement from trajectory-driven self-evolution
- Closed-loop: historical trajectory → skill extraction → repair generation → validation → skill update
- Demonstrates feasible self-evolving agent without external supervision

## Limitations
Not explicitly stated in notes.

## Optics_agent Lessons
- **Long-term architecture blueprint**: every COMSOL simulation trajectory automatically evolves skills
- Each failed simulation → structured反思提取 → skill library update → improved next attempt
- Trajectory distillation pattern directly applicable to COMSOL parameter tuning experience
- Self-evolving library pattern (SoK Pattern #3) realized in practice
- Current gap: optics_agent has no对应闭环引擎
