"""训练配置 —— Agent-07 名下文件（主树 train/config.py 的工作区镜像）。

单一事实来源：`TrainConfig` 字段默认值即基线超参；`DEFAULT_BASELINE`
在模块底部由 `asdict(TrainConfig())` 导出，避免双份维护。

量级理由（DEFAULT_BASELINE 逐项）见各类字段的行内注释；
加载方式：Python dict（`from_dict`）/ JSON 文件（`from_json`，
如 `--config train/configs/baseline.json`）。
"""

from __future__ import annotations

import dataclasses
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class TrainConfig:
    """PPO 训练全量配置（mock 期与真实环境共用一套）。"""

    # ---- PPO 超参 ----
    # rollout 长度。RA2 单局长（max_episode_steps=20000）且奖励密集，
    # rollout 不必覆盖整局；256 步一次更新，1e5 步 mock 验证可得约 390
    # 次更新，足以观察 loss 下降。Phase 2 真实环境吞吐受限时可调大。
    n_steps: int = 256
    # minibatch 大小。取 n_steps*n_envs=256 的因子，PPO 经典取值。
    batch_size: int = 64
    # 每批数据的 epoch 数，SB3 默认推荐值。
    n_epochs: int = 10
    # 折扣因子。契约规定 VecNormalize 用 γ=0.99，两者必须一致，
    # 故共用同一字段（train_ppo 构造 VecNormalize 时取 gamma）。
    gamma: float = 0.99
    # GAE λ，偏差/方差折中，SB3 默认。
    gae_lambda: float = 0.95
    # 熵系数。动作 12 个且近半为 no-op，保留探索压力避免过早塌缩到 no-op。
    ent_coef: float = 0.01
    vf_coef: float = 0.5        # 价值损失系数，SB3 默认。
    max_grad_norm: float = 0.5  # 梯度裁剪，SB3 默认。
    learning_rate: float = 3e-4  # Adam 步长，PPO 通用起点，Phase 2 再调。
    clip_range: float = 0.2      # PPO 裁剪范围，SB3 默认。

    # ---- 环境 ----
    # auto: 尝试导入 ra2_env.RA2Env，不可用则回退 mock 并告警；
    # mock: 强制内置 MockRA2Env（管线冒烟/CI 用）；
    # real: 强制真实环境，导入失败直接报错（不静默降级）。
    env_backend: str = "auto"
    base_url: str = "http://localhost:8000"  # openra-rl server 地址
    max_episode_steps: int = 20000           # 契约 v1：RA2Env 默认值
    # 真实环境是否包 SupervisedEnv（Agent-05）。mock 不需要也从不包。
    use_supervised_env: bool = True

    # ---- mock env 参数（Agent-02 公布观测维度后对齐 MOCK_OBS_DIM）----
    mock_obs_dim: int = 64    # 占位维度，待 Agent-02 BOARD 公布后调整
    mock_n_actions: int = 12  # 契约 v1：Discrete N ∈ [10, 16]，取中值
    mock_episode_steps: int = 200  # mock 局短，快速验证管线

    # ---- 训练预算 ----
    # Phase 2 基线预算起点（击败 Easy AI）；mock 验证用 CLI 覆写为 1e5。
    total_timesteps: int = 1_000_000
    seed: int = 42

    # ---- 路径（checkpoints/ 与 runs/ 均已 gitignore）----
    checkpoint_dir: str = "checkpoints"
    tb_log_dir: str = "runs/tensorboard"
    # 缺省用 ppo_<backend>_<时间戳>，见 train_ppo.default_run_name()
    run_name: str = ""

    # ---- VecNormalize（契约：norm obs+reward，clip 10，γ=0.99）----
    norm_obs: bool = True
    norm_reward: bool = True
    clip_obs: float = 10.0
    clip_reward: float = 10.0

    # ---- checkpoint / eval（均以"每个向量环境步"计，n_envs=1 时即环境步）----
    checkpoint_freq: int = 20_000  # 每 2 万步存一次，断点粒度与评估对齐
    eval_freq: int = 20_000        # 评估频率（EvalCallback 自动同步归一化统计）
    n_eval_episodes: int = 5       # mock 快；真实环境一局分钟级，Phase 2 调低
    eval_seed: int = 0

    # ---- 课程表（Agent-04 weight_schedule 未定，默认关）----
    # 开启后由 CurriculumCallback 按训练进度调用环境侧
    # set_reward_progress(progress)；机制与 01/04 在 BOARD 对齐。
    curriculum: bool = False

    # ------------------------------------------------------------------
    # 校验与序列化
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.env_backend not in ("auto", "mock", "real"):
            raise ValueError(f"env_backend 必须是 auto/mock/real，得到 {self.env_backend!r}")
        if not 0.0 < self.gamma < 1.0:
            raise ValueError(f"gamma 必须在 (0,1)，得到 {self.gamma}")
        if not 0.0 <= self.gae_lambda <= 1.0:
            raise ValueError(f"gae_lambda 必须在 [0,1]，得到 {self.gae_lambda}")
        for name in ("n_steps", "batch_size", "n_epochs", "total_timesteps",
                     "checkpoint_freq", "eval_freq", "n_eval_episodes",
                     "mock_obs_dim", "max_episode_steps"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} 必须为正数，得到 {getattr(self, name)}")
        if not 10 <= self.mock_n_actions <= 16:
            raise ValueError(f"mock_n_actions 须在契约范围 [10,16]，得到 {self.mock_n_actions}")
        if self.n_steps % self.batch_size != 0 and self.batch_size % self.n_steps != 0:
            # batch 必须整除 rollout 缓冲（n_steps*n_envs），否则 SB3 报错
            raise ValueError(
                f"batch_size={self.batch_size} 与 n_steps={self.n_steps} 须互相整除"
                "（n_envs=1 时缓冲=n_steps）")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save_json(self, path: str | Path) -> Path:
        """把解析后的最终配置落盘，供 RUNS.md 追溯与断点续训复现。"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        return path

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainConfig":
        """从 dict 构造：未知键报错（防拼写错误静默失效），缺省键用默认值。"""
        valid = {f.name for f in dataclasses.fields(cls)}
        unknown = set(data) - valid
        if unknown:
            raise ValueError(f"TrainConfig 未知字段: {sorted(unknown)}")
        return cls(**data)

    @classmethod
    def from_json(cls, path: str | Path) -> "TrainConfig":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


# 基线超参单一来源：TrainConfig 默认值。理由见字段行内注释。
DEFAULT_BASELINE: Dict[str, Any] = asdict(TrainConfig())
