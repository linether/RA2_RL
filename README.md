# RA2_RL

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Phase%200-orange.svg)
![Project](https://img.shields.io/badge/project-public-blueviolet.svg)

English | [中文](README.zh-CN.md)

A research and engineering project for building a Reinforcement Learning environment around Red Alert 2: Yuri's Revenge.

This repository aims to provide a clean bridge from the original game runtime to a Gymnasium-style interface, with RL training entry points and a realistic validation path for both original-game and OpenRA-based experiments.

## Why this project exists

Most public RTS RL efforts either:

- depend on a custom game environment or emulator that is not the original game,
- focus on agent logic without a reusable training environment, or
- stop at a one-off prototype without a stable environment abstraction.

This project is trying to do the harder but more useful thing: make the original game playable as a real training environment while keeping the interface clean enough for RL experimentation.

## Current status

As of 2026-09-01, the project is in a strong validation phase:

- Phase 0 environment validation is considered complete for the original-game path.
- The project has verified a working two-track strategy:
  - Track A: OpenRA-RL as the main training path
  - Track B: ra2yrcpp / pyra2yr as a fidelity-validation path for the original game
- The remaining primary milestone is Phase 1: a minimal Gymnasium environment and a stable random-agent stress test.

See [docs/roadmap.md](docs/roadmap.md) and [CLAUDE.md](CLAUDE.md) for the current project state, constraints, and execution notes.

## Architecture

```text
RL Training Stack
    ↓
RA2Env (Gymnasium-style interface)
    ↓
State / Action / Reward adapters
    ↓
Original-game bridge (ra2yrcpp / pyra2yr)
    ↓
Yuri's Revenge game process
```

The repository is structured around a dual-track strategy:

- Track A: OpenRA-RL for headless and fast experimental iteration
- Track B: ra2yrcpp for original-game fidelity, validation, and replay-oriented checks

## Related ecosystem

This project sits in a broader ecosystem of RTS AI and research tooling:

- [OpenRA-RL](https://github.com/yxc20089/OpenRA-RL) — active project building a Python environment and agent stack around OpenRA
- [ra2yrcpp](https://github.com/shmocz/ra2yrcpp) — low-level game-process bridge for Yuri's Revenge
- [pyra2yr](https://github.com/shmocz/pyra2yr) — Python client layer around ra2yrcpp
- [Stable Baselines 3](https://stable-baselines3.readthedocs.io/) — RL training backend

Compared with those projects, this repository is intentionally positioned as the glue layer: original-game access + standardized RL interface + reproducible training workflow.

## Project structure

```text
RA2_RL/
├── README.md
├── README.zh-CN.md
├── CLAUDE.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── pyproject.toml
├── requirements/
├── requirements.txt
├── src/
│   └── ra2_rl/
│       └── env/
├── configs/
│   ├── README.md
│   └── runtime/
├── examples/
│   └── README.md
├── scripts/
├── tests/
├── train/
│   ├── README.md
│   ├── __init__.py
│   ├── train_ppo.py
│   └── configs/
│       ├── README.md
│       └── baseline.json
├── eval/
│   └── README.md
├── ra2_env/
├── docs/
│   ├── architecture.md
│   ├── architecture.zh-CN.md
│   ├── roadmap.md
│   ├── roadmap.zh-CN.md
│   ├── technical-notes.md
│   ├── technical-notes.zh-CN.md
│   └── adr/
├── agents/
│   ├── README.md
│   ├── BOARD.md
│   └── agent-*/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
└── .gitignore
```

## Quick start

### Dependencies

- Python 3.10+
- Windows 10/11 for the original-game validation path
- A clean Yuri's Revenge installation for Track B testing
- OpenRA-RL environment for Track A development

### Install

```bash
pip install -r requirements.txt
```

For technical constraints and environment setup, see:

- [docs/technical-notes.md](docs/technical-notes.md)
- [docs/roadmap.md](docs/roadmap.md)
- [docs/architecture.md](docs/architecture.md)

## Roadmap

### Phase 0 — Environment validation

- Validate both original-game and OpenRA-based routes
- Confirm state access and command execution
- Establish the architecture and constraints

### Phase 1 — Minimal Gym environment

- Implement RA2Env with reset / step / close
- Standardize observation and action spaces
- Pressure-test with a random policy

### Phase 2 — Baseline training

- Add PPO baseline and training configuration
- Keep evaluation reproducible and comparable

### Phase 3+ — Enrichment and scaling

- Observation/action improvement
- Reward shaping and training robustness
- Infrastructure and deployment improvements

## Documentation

- [docs/architecture.md](docs/architecture.md) — architecture and system decomposition
- [docs/architecture.zh-CN.md](docs/architecture.zh-CN.md) — architecture overview in Chinese
- [docs/roadmap.md](docs/roadmap.md) — current roadmap and milestone tracking
- [docs/roadmap.zh-CN.md](docs/roadmap.zh-CN.md) — roadmap in Chinese
- [docs/technical-notes.md](docs/technical-notes.md) — constraints, caveats, and environment notes
- [docs/technical-notes.zh-CN.md](docs/technical-notes.zh-CN.md) — technical notes in Chinese
- [docs/adr/](docs/adr/) — architecture decision records
- [agents/README.md](agents/README.md) — multi-agent collaboration rules and conventions

## Contributing

Contributions are welcome, especially on:

- RL environment design
- observation/action-space improvements
- reward engineering
- recovery and stability tooling
- evaluation and benchmarking
- project documentation and reproducibility

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, commit conventions, and contribution guidelines.

## Security

If you discover a vulnerability or security-sensitive issue, please do not open a public issue. See [SECURITY.md](SECURITY.md).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Acknowledgements

- Red Alert 2: Yuri's Revenge
- ra2yrcpp and pyra2yr
- OpenRA-RL
- Gymnasium and Stable Baselines 3
