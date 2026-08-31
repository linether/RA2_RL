# Training

This directory contains the project-level training entry points and configuration presets.

## Purpose

- host the top-level PPO and policy training workflow
- keep reusable training configuration under version control
- provide a clean boundary between environment code and training logic

## Layout

- `__init__.py` — package marker
- `configs/` — JSON/YAML configuration files for training runs
- `train_ppo.py` — main training entry point for PPO workflows

## Typical usage

```bash
python -m train.train_ppo --env mock --total-timesteps 100000
python -m train.train_ppo --config train/configs/baseline.json
```
