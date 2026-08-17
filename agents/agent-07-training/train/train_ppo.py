"""PPO 训练主入口 —— Agent-07 名下文件（主树 train/train_ppo.py 的工作区镜像）。

管线：RA2Env(Agent-01) → [SupervisedEnv(Agent-05)] → Monitor → DummyVecEnv
      → VecNormalize → PPO(MlpPolicy) + {Checkpoint, Eval, Curriculum} 回调
      → TensorBoard 日志 runs/tensorboard/ + checkpoints/。

mock 期：内置 MockRA2Env（同 Gymnasium API 契约、线性可控合成奖励），
验证的是管线本身（VecNormalize 统计量 / checkpoint / resume / TB），
不是策略强度。Agent-01/05 集成后 `--env real` 即切真实环境。

用法（仓库根目录）：
    python -m train.train_ppo --env mock --total-timesteps 100000 --run-name mock-1e5
    python -m train.train_ppo --config train/configs/baseline.json
    python -m train.train_ppo --env mock --resume checkpoints/ppo_run_20000_steps.zip

设计约束（TASK.md 技术要点）：
- n_envs=1 DummyVecEnv；SubprocVecEnv 并行留作 Phase 4。
- 环境异常不在本文件捕获（ SupervisedEnv 负责兜底），只处理 Ctrl-C 落盘。
"""

from __future__ import annotations

import argparse
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

# 支持 `python train/train_ppo.py` 直接执行（仓库根为准）
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    BaseCallback,
    CheckpointCallback,
    EvalCallback,
)
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecEnv, VecNormalize

from train.config import TrainConfig

logger = logging.getLogger("train_ppo")

# Agent-02 公布观测维度前的占位常量（与 TrainConfig.mock_obs_dim 默认一致）
MOCK_OBS_DIM = 64
MOCK_N_ACTIONS = 12


# ---------------------------------------------------------------------------
# Mock 环境：契约签名 + 线性可控合成奖励
# ---------------------------------------------------------------------------
class MockRA2Env(gym.Env):
    """一维"追靶"任务，API 与 RA2Env 契约一致（reset/step/observation_space/…）。

    - 状态 s、目标 t ∈ [-1,1]；obs = [s, t, 进度, 噪声…]（噪声使
      VecNormalize 各维统计量真实演化，验证归一化管线）。
    - 奖励线性可控：r = -|s-t| - 0.005。随机策略 ep_rew ≈ -0.75*T，
      最优 ≈ -0.005*T，1e5 步内 PPO 的 ep_rew_mean 应显著抬升。
    - 动作 12 个：0/1 = ±0.2 粗调，2/3 = ±0.05 微调，4..11 = no-op
      （保留无效动作，贴近真实动作空间结构，测探索）。
    """

    metadata = {"render_modes": []}

    def __init__(self, obs_dim: int = MOCK_OBS_DIM,
                 n_actions: int = MOCK_N_ACTIONS,
                 max_episode_steps: int = 200) -> None:
        super().__init__()
        assert obs_dim >= 3
        self.obs_dim = obs_dim
        self.max_episode_steps = max_episode_steps
        self.observation_space = gym.spaces.Box(
            low=-2.0, high=2.0, shape=(obs_dim,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(n_actions)
        self._state = 0.0
        self._target = 0.0
        self._step_count = 0
        self._rng = np.random.default_rng()

    def _obs(self) -> np.ndarray:
        obs = self._rng.normal(0.0, 0.1, size=self.obs_dim).astype(np.float32)
        obs[0] = self._state
        obs[1] = self._target
        obs[2] = self._step_count / self.max_episode_steps
        return obs

    def reset(self, *, seed: Optional[int] = None,
              options: Optional[dict] = None):
        super().reset(seed=seed)
        # reset(seed) 之后 self.np_random 已就绪，供 action_space/sample 用
        self._state = float(self.np_random.uniform(-1.0, 1.0))
        self._target = float(self.np_random.uniform(-1.0, 1.0))
        self._step_count = 0
        return self._obs(), {}

    def step(self, action: int):
        delta = {0: -0.2, 1: +0.2, 2: -0.05, 3: +0.05}.get(int(action), 0.0)
        self._state = float(np.clip(self._state + delta, -1.0, 1.0))
        self._step_count += 1
        dist = abs(self._state - self._target)
        reward = -dist - 0.005
        terminated = False
        truncated = self._step_count >= self.max_episode_steps
        return self._obs(), reward, terminated, truncated, {"dist": dist}


# ---------------------------------------------------------------------------
# 环境构造
# ---------------------------------------------------------------------------
def make_raw_env(cfg: TrainConfig) -> gym.Env:
    """按 backend 构造裸环境（Monitor/Vec 包装在外的层做）。

    auto：能导入 RA2Env 就用真实环境，否则告警回退 mock（集成过渡期）。
    real：导入失败直接抛错 —— 真实训练绝不能静默跑在 mock 上。
    """
    if cfg.env_backend in ("real", "auto"):
        try:
            from ra2_env.env import RA2Env  # Agent-01 名下
        except ImportError as exc:
            if cfg.env_backend == "real":
                raise RuntimeError(
                    "--env real 但 ra2_env.RA2Env 不可用（Agent-01 未集成？）"
                ) from exc
            logger.warning("ra2_env 不可用（%s），auto 回退 mock 环境", exc)

        else:
            env: gym.Env = RA2Env(base_url=cfg.base_url,
                                  max_episode_steps=cfg.max_episode_steps)
            if cfg.use_supervised_env:
                try:
                    from ra2_env.recovery import SupervisedEnv  # Agent-05 名下
                except ImportError as exc:
                    raise RuntimeError(
                        "use_supervised_env=True 但 ra2_env.recovery.SupervisedEnv"
                        " 不可用（Agent-05 未集成？）；请先集成 05 或在 config 关闭"
                    ) from exc
                env = SupervisedEnv(env)  # 契约：包装，不改被包装类
            return env
    return MockRA2Env(obs_dim=cfg.mock_obs_dim, n_actions=cfg.mock_n_actions,
                      max_episode_steps=cfg.mock_episode_steps)


# n_envs=1（DummyVecEnv）；SubprocVecEnv 留作 Phase 4（TASK 技术要点）。
# checkpoint/eval 频率按"环境步"语义换算成向量步。
N_ENVS = 1


def make_vec_env(cfg: TrainConfig) -> VecEnv:
    def _thunk() -> gym.Env:
        # Monitor 无文件名：ep_rew/ep_len 经 info buffer 进 SB3 logger 与 TB
        return Monitor(make_raw_env(cfg))
    return DummyVecEnv([_thunk for _ in range(N_ENVS)])


def wrap_vec_normalize(cfg: TrainConfig, venv: VecEnv,
                       stats_path: Optional[Path] = None) -> VecNormalize:
    """新建或从 stats 文件恢复 VecNormalize。

    契约：norm obs+reward，clip 10，γ=0.99（gamma 与 PPO 共用 cfg.gamma）。
    """
    if stats_path is not None and stats_path.exists():
        logger.info("加载 VecNormalize 统计量: %s", stats_path)
        return VecNormalize.load(str(stats_path), venv)
    return VecNormalize(venv, training=True, norm_obs=cfg.norm_obs,
                        norm_reward=cfg.norm_reward, clip_obs=cfg.clip_obs,
                        clip_reward=cfg.clip_reward, gamma=cfg.gamma)


def make_eval_env(cfg: TrainConfig) -> VecNormalize:
    """独立评估环境：training=False（只读统计量），不归一化奖励。

    EvalCallback 每次评估前自动调用 sync_envs_normalization 同步训练侧
    统计量，无需手工对齐。
    """
    eval_env = make_vec_env(cfg)
    return VecNormalize(eval_env, training=False, norm_obs=cfg.norm_obs,
                        norm_reward=False, clip_obs=cfg.clip_obs,
                        gamma=cfg.gamma)


# ---------------------------------------------------------------------------
# 回调
# ---------------------------------------------------------------------------
class CurriculumCallback(BaseCallback):
    """课程表钩子：把训练进度通知环境侧，驱动 reward 权重更新。

    机制待与 Agent-01/04 在 BOARD 对齐（契约 v1 只有
    RewardFunction.weights()，尚无 setter 协议）。当前约定：
    若 Monitor 内层环境暴露 ``set_reward_progress(progress: float)``
    则每个 rollout 调用一次；未暴露则跳过。cfg.curriculum=False 关闭。
    """

    def __init__(self) -> None:
        super().__init__()
        self._hooks: list[Callable[[float], None]] = []

    def _on_training_start(self) -> None:
        for env in getattr(self.training_env, "envs", []):  # DummyVecEnv
            inner = getattr(env, "env", env)  # 剥 Monitor
            fn = getattr(inner, "set_reward_progress", None)
            if callable(fn):
                self._hooks.append(fn)
        if self._hooks:
            logger.info("课程表钩子挂接 %d 个环境", len(self._hooks))
        else:
            logger.debug("无环境实现 set_reward_progress，课程表为空操作")

    def _on_rollout_end(self) -> None:
        if self.model.num_timesteps <= 0 or self._total_timesteps <= 0:
            return
        progress = min(1.0, self.model.num_timesteps / self._total_timesteps)
        for fn in self._hooks:
            fn(progress)


def build_callbacks(cfg: TrainConfig, run_ckpt_dir: Path):
    # save_freq 以向量步计（n_calls 每向量步 +1）；n_envs=1 时与环境步等价
    ckpt = CheckpointCallback(
        save_freq=max(1, cfg.checkpoint_freq // N_ENVS),
        save_path=str(run_ckpt_dir),
        name_prefix="ppo",
        save_vecnormalize=True,  # 每个checkpoint旁存vecnormalize.pkl，resume成对加载
    )
    # 评估：暂用 SB3 内置 deterministic rollout；Agent-08 的
    # evaluate(policy, env, n_episodes, seed) 集成后切自定义回调（BOARD 协调）。
    eval_cb = EvalCallback(
        make_eval_env(cfg),
        best_model_save_path=str(run_ckpt_dir / "best"),
        eval_freq=max(1, cfg.eval_freq // N_ENVS),
        n_eval_episodes=cfg.n_eval_episodes,
        deterministic=True,
    )
    callbacks = [ckpt, eval_cb]
    if cfg.curriculum:
        callbacks.append(CurriculumCallback())
    return callbacks


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def git_short_hash() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def default_run_name(cfg: TrainConfig) -> str:
    if cfg.run_name:
        return cfg.run_name
    return f"ppo_{cfg.env_backend}_{datetime.now():%Y%m%d-%H%M%S}"


def build_model(cfg: TrainConfig, vec_env: VecNormalize,
                resume_path: Optional[str]) -> tuple[PPO, bool]:
    """新建或恢复模型。返回 (model, resumed)。

    resume 时 reset_num_timesteps=False：total_timesteps 按绝对步数解释，
    SB3 的 num_timesteps / 进度调度（lr、clip 衰减）从 checkpoint 无缝续接。
    """
    if resume_path:
        model = PPO.load(resume_path, env=vec_env)
        logger.info("恢复模型 %s（num_timesteps=%d）",
                    resume_path, model.num_timesteps)
        return model, True
    return PPO(
        "MlpPolicy", vec_env, verbose=1,
        n_steps=cfg.n_steps, batch_size=cfg.batch_size, n_epochs=cfg.n_epochs,
        gamma=cfg.gamma, gae_lambda=cfg.gae_lambda, ent_coef=cfg.ent_coef,
        vf_coef=cfg.vf_coef, max_grad_norm=cfg.max_grad_norm,
        learning_rate=cfg.learning_rate, clip_range=cfg.clip_range,
        seed=cfg.seed, tensorboard_log=cfg.tb_log_dir,
    ), False


def find_stats_for_checkpoint(resume_path: Path,
                              fallback: Optional[Path] = None) -> Optional[Path]:
    """定位与 checkpoint 配套的 VecNormalize 统计量。

    优先级：CheckpointCallback 成对保存的 ppo_vecnormalize_<N>_steps.pkl
    （与该 checkpoint 严格同步）> 同目录 vecnormalize.pkl（最终/中断保存，
    可能比 checkpoint 新）> fallback（当前 run 目录）。
    """
    candidates: list[Path] = []
    m = re.match(r"^(.+?)_(\d+)_steps$", resume_path.stem)
    if m:
        prefix, steps = m.groups()
        candidates.append(resume_path.parent / f"{prefix}_vecnormalize_{steps}_steps.pkl")
    candidates.append(resume_path.parent / "vecnormalize.pkl")
    if fallback is not None:
        candidates.append(fallback)
    for c in candidates:
        if c.exists():
            return c
    return None


def train(cfg: TrainConfig, resume_path: Optional[str] = None) -> Path:
    run_name = default_run_name(cfg)
    run_ckpt_dir = Path(cfg.checkpoint_dir) / run_name
    run_ckpt_dir.mkdir(parents=True, exist_ok=True)
    stats_path = run_ckpt_dir / "vecnormalize.pkl"

    logger.info("run=%s backend=%s git=%s total_timesteps=%d resume=%s",
                run_name, cfg.env_backend, git_short_hash(),
                cfg.total_timesteps, resume_path or "-")
    cfg.save_json(run_ckpt_dir / "config.json")  # 运行清单追溯用

    venv = make_vec_env(cfg)
    load_stats = None
    if resume_path:
        load_stats = find_stats_for_checkpoint(Path(resume_path), stats_path)
        if load_stats is None:
            logger.warning("未找到 VecNormalize 统计量文件，从零初始化（统计量断链！）")
    vec_env = wrap_vec_normalize(cfg, venv, load_stats)

    model, resumed = build_model(cfg, vec_env, resume_path)
    callbacks = build_callbacks(cfg, run_ckpt_dir)

    try:
        model.learn(
            total_timesteps=cfg.total_timesteps,
            callback=callbacks, tb_log_name=run_name,
            reset_num_timesteps=not resumed,  # 续训按绝对步数推进
            progress_bar=False,
        )
    except KeyboardInterrupt:
        logger.warning("收到中断，保存模型后退出（不吞环境异常，仅处理 SIGINT）")
        model.save(run_ckpt_dir / "interrupted")
        vec_env.save(str(stats_path))
        raise

    final_path = run_ckpt_dir / "final_model"
    model.save(final_path)
    vec_env.save(str(stats_path))
    logger.info("完成：model=%s.zip stats=%s", final_path, stats_path)
    return final_path


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="RA2 PPO 训练主入口（Agent-07）")
    p.add_argument("--config", type=str, default=None,
                   help="JSON 配置文件（如 train/configs/baseline.json）；缺省用内置 DEFAULT_BASELINE")
    p.add_argument("--env", choices=["auto", "mock", "real"], default=None,
                   help="覆盖 config 的 env_backend")
    p.add_argument("--resume", type=str, default=None,
                   help="checkpoint .zip 路径（自动加载同目录 vecnormalize.pkl）")
    p.add_argument("--total-timesteps", type=int, default=None,
                   help="覆盖 config 的训练总步数")
    p.add_argument("--run-name", type=str, default=None, help="运行名（TB/checkpoint 子目录）")
    p.add_argument("--seed", type=int, default=None, help="覆盖 config 的随机种子")
    p.add_argument("--device", type=str, default="auto", help="torch device")
    return p.parse_args(argv)


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s")
    args = parse_args(argv)

    if args.config:
        cfg = TrainConfig.from_json(args.config)
    else:
        cfg = TrainConfig()
    if args.env:
        cfg.env_backend = args.env
    if args.total_timesteps is not None:
        cfg.total_timesteps = args.total_timesteps
    if args.run_name:
        cfg.run_name = args.run_name
    if args.seed is not None:
        cfg.seed = args.seed
    cfg.validate()

    train(cfg, resume_path=args.resume)
    return 0


if __name__ == "__main__":
    sys.exit(main())
