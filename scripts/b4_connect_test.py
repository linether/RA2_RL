"""B4: connectivity test against a running ra2yrcpp game (port 14521).

Launch gamemd-spawn-ra2yrcpp.exe -SPAWN first, then run this with the
ra2rl-b venv python. Prints per-frame state samples and exits when the
game ends.

Note: pyra2yr 0.3.0 mainloop crashes if get_state() times out (s=None hits
should_update). During map loading the in-game command queue isn't running
yet, so timeouts are expected — patch should_update to tolerate None.
"""

import asyncio
import logging

from pyra2yr.manager import Manager
from pyra2yr.state_manager import StateManager
from pyra2yr.util import setup_logging
from ra2yrproto import ra2yr

_orig_should_update = StateManager.should_update
StateManager.should_update = (
    lambda self, s: s is not None and _orig_should_update(self, s)
)


async def main():
    setup_logging(level=logging.INFO)
    M = Manager(address="127.0.0.1", port=14521, fetch_state_timeout=10.0)
    M.start()
    print("[B4] manager started, waiting for game to begin (loading ~15s)...")
    await M.M.wait_game_to_begin(timeout=180)
    print("[B4] GAME BEGAN, stage:", M.state.s.stage)

    for i in range(60):
        s = M.state.s
        houses = [
            (h.name, h.money, int(h.power_output), bool(h.defeated), bool(h.is_game_over))
            for h in s.houses
        ]
        print(f"[B4] stage={s.stage} frame={s.current_frame} objects={len(s.objects)} houses={houses}", flush=True)
        if s.stage == ra2yr.STAGE_EXIT_GAME:
            break
        await asyncio.sleep(1.0)

    print("[B4] waiting for game to exit (up to 300s)...")
    try:
        await M.M.wait_game_to_exit(timeout=300)
        print("[B4] GAME EXITED normally, final frame:", M.state.s.current_frame)
    except Exception as e:
        print("[B4] wait_game_to_exit:", repr(e))
    await M.stop()
    print("[B4] done")


if __name__ == "__main__":
    asyncio.run(main())
