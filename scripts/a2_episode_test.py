"""A2: run one headless OpenRA-RL episode via the OpenEnv client.

Requires the game server running (openra-rl server start, port 8000).
Plays idle (no-op actions) until the episode ends or a step cap is hit.
Run with the ra2rl venv python.
"""

import asyncio

from openra_env.client import OpenRAEnv
from openra_env.models import OpenRAAction

MAX_STEPS = 30000


async def main():
    async with OpenRAEnv(base_url="http://localhost:8000") as env:
        print("[A2] connected, resetting (may take 60-120s)...")
        result = await env.reset()
        obs = result.observation
        print(f"[A2] reset done: tick={obs.tick} cash={obs.economy.cash} "
              f"units={len(obs.units)} buildings={len(obs.buildings)}")

        step = 0
        while not result.done and step < MAX_STEPS:
            result = await env.step(OpenRAAction(commands=[]))
            step += 1
            obs = result.observation
            if step % 500 == 0 or result.done:
                print(f"[A2] step={step} tick={obs.tick} cash={obs.economy.cash} "
                      f"units={len(obs.units)} buildings={len(obs.buildings)} "
                      f"enemies={len(obs.visible_enemies)} reward={result.reward} "
                      f"done={result.done} result={obs.result!r}", flush=True)

        print(f"[A2] EPISODE END: steps={step} done={result.done} "
              f"result={obs.result!r} reward={result.reward}")


if __name__ == "__main__":
    asyncio.run(main())
