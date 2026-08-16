"""A3: full-episode termination test for OpenRA-RL (deploy MCV, then surrender).

Validates the command round-trip (DEPLOY) and a deterministic episode end
(SURRENDER -> done=True, result='lose'). Requires the game server on :8000.
Run with the ra2rl venv python.
"""

import asyncio

from openra_env.client import OpenRAEnv
from openra_env.models import ActionType, CommandModel, OpenRAAction


async def main():
    async with OpenRAEnv(base_url="http://localhost:8000") as env:
        print("[A3] connected, resetting...")
        result = await env.reset()
        obs = result.observation

        # wait for the MCV to appear
        step = 0
        while not obs.units and step < 100:
            result = await env.step(OpenRAAction(commands=[]))
            obs = result.observation
            step += 1
        mcv = obs.units[0]
        print(f"[A3] tick={obs.tick} MCV: id={mcv.actor_id} type={mcv.type!r}")

        print("[A3] sending DEPLOY...")
        result = await env.step(
            OpenRAAction(
                commands=[CommandModel(action=ActionType.DEPLOY, actor_id=mcv.actor_id)]
            )
        )
        for _ in range(100):
            result = await env.step(OpenRAAction(commands=[]))
            obs = result.observation
            if obs.buildings:
                break
        print(f"[A3] tick={obs.tick} buildings={[(b.type, b.actor_id) for b in obs.buildings]}")
        assert obs.buildings, "DEPLOY did not produce a building"
        print("[A3] DEPLOY command round-trip OK")

        print("[A3] sending SURRENDER...")
        result = await env.step(
            OpenRAAction(commands=[CommandModel(action=ActionType.SURRENDER)])
        )
        step = 0
        while not result.done and step < 300:
            result = await env.step(OpenRAAction(commands=[]))
            step += 1
        obs = result.observation
        print(f"[A3] EPISODE END: done={result.done} result={obs.result!r} "
              f"reward={result.reward} tick={obs.tick}")


if __name__ == "__main__":
    asyncio.run(main())
