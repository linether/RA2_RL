"""B3: generate spawn.ini + spawnmap.ini for the clean test dir (Ra2Game412-rl).

1 human host (ws_port 14521, matches ra2yrcpp.json) vs 1 AI skirmish on
pyra2yr's bundled arctic_circle.map. Run with the ra2rl-b venv python.
"""

from pathlib import Path

import pyra2yr
from pyra2yr.game import MultiGameInstanceConfig

GAME_DIR = Path(r"E:\Project\Claude Code\RA2_RL\Ra2Game412-rl")
PKG_DATA = Path(pyra2yr.__file__).parent / "data"

cfg = MultiGameInstanceConfig.from_dict(
    {
        "scenario": {
            "map_path": str(PKG_DATA / "arctic_circle.map"),
            "seed": 123,
            "game_speed": 0,
            "start_credits": 10000,
            "short_game": True,
            "ra2_mode": False,
        },
        "players": [
            {
                "name": "player_0",
                "color": "Red",
                "side": "1",
                "location": 0,
                "is_host": True,
                "ws_port": 14521,
            },
            {
                "name": "ai_1",
                "color": "Yellow",
                "side": "6",
                "location": 1,
                "ai_difficulty": 2,
            },
        ],
    }
)

spawn_ini = cfg.to_ini(0)
(GAME_DIR / "spawn.ini").write_text(spawn_ini, encoding="latin-1")

map_text = (PKG_DATA / "arctic_circle.map").read_text(encoding="latin-1")
(GAME_DIR / "spawnmap.ini").write_text(map_text, encoding="latin-1")

print(spawn_ini)
print(f"spawnmap.ini: {len(map_text)} chars written")
