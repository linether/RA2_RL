# Contributing to RA2_RL

Thanks for your interest in contributing to this project.

This repository is a research-oriented RL and RTS environment project. Contributions are welcome in the areas of environment design, training experiments, evaluation, documentation, tooling, and reproducibility.

## Project scope

The project focuses on building a training-ready environment around Red Alert 2: Yuri's Revenge, with a clean RL interface and reproducible training workflow.

Current priorities include:

- minimal Gymnasium-style environment implementation
- stable observation / action interfaces
- reward shaping and episode termination logic
- crash recovery and robustness
- evaluation and benchmark tooling
- documentation and project onboarding

## Before you start

1. Read the main project overview in [README.md](README.md).
2. Review the project architecture in [docs/architecture.md](docs/architecture.md).
3. Check the roadmap in [docs/roadmap.md](docs/roadmap.md).
4. For large multi-agent or cross-module work, read [agents/README.md](agents/README.md) first.

## Development workflow

### 1. Fork and branch

Create a feature branch from the main branch:

```bash
git checkout -b feature/my-improvement
```

### 2. Keep changes focused

Prefer small, reviewable changes. A single PR should usually resolve one problem or add one coherent capability.

### 3. Validate locally

At minimum, run the relevant tests or smoke checks before opening a PR:

```bash
pytest
```

If your change affects project structure or docs, ensure the README and architecture notes remain consistent.

### 4. Open a pull request

When opening a PR, include:

- a short summary of the change
- the motivation or problem it solves
- any environment assumptions or dependencies
- validation steps performed

## Coding conventions

- Write clear, readable Python code.
- Keep module boundaries consistent with the current project structure.
- Favor explicit interfaces over hidden magic.
- Avoid introducing environment-specific assumptions into core abstractions unless necessary.
- Preserve reproducibility and document any setup caveats.

## Commit conventions

Use clear, conventional-style commit messages when possible:

- `feat:` for new functionality
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for tests
- `chore:` for maintenance work

Example:

```bash
git commit -m "feat(env): add minimal RA2Env API"
```

## Environment and safety constraints

This project deals with real game software and game-process instrumentation. Some work can be sensitive or platform-specific.

Please do not:

- modify original game directories unless explicitly required by the project workflow
- leave game processes running after a validation session
- commit large binary or external game artifacts
- bypass the project’s clean-environment rules without documenting it

## Documentation improvements

Documentation is part of the project value. If you improve:

- architecture notes
- environment setup
- training experiments
- debugging notes
- contributor onboarding

please include a matching explanation in the pull request.

## Questions

If you are unsure whether a contribution fits the project direction, open a discussion or issue first.

We welcome research ideas, engineering improvements, and reproducible experiments.
