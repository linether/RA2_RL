"""B5 supplement: verify we can issue commands (deploy MCV) via ra2yrcpp.

Launch gamemd-spawn-ra2yrcpp.exe -SPAWN first. Exits as soon as the deploy
round-trip is confirmed (a building appears for the current player).
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
    print("[B5] waiting for game to begin...")
    await M.M.wait_game_to_begin(timeout=180)
    p = M.state.current_player()
    print(f"[B5] game began, current player: {p.name!r} faction={p.faction!r}")

    objs = list(M.state.query_objects(h=p))
    for o in objs:
        print(f"[B5] own object: {o.get()}")
    if not objs:
        raise RuntimeError("no objects for current player")

    mcv = objs[0]
    print("[B5] sending deploy command for MCV...")
    await M.M.deploy(mcv.o)

    def has_building():
        return (
            len(list(M.state.query_objects(h=p, a=ra2yr.ABSTRACT_TYPE_BUILDING))) >= 1
        )

    await M.wait_state(has_building, timeout=60)
    b = next(M.state.query_objects(h=p, a=ra2yr.ABSTRACT_TYPE_BUILDING))
    print(f"[B5] SUCCESS: building present at frame {M.state.s.current_frame}")
    print(f"[B5] building: {b.get()}")
    await M.stop()
    print("[B5] done")


if __name__ == "__main__":
    asyncio.run(main())
