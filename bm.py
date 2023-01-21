from mastermind import sol, Solution, isol
from mastermind.adversory import AutoMaster, AutoPlayer, PosStrategy
from mastermind.game import play_game
import numpy as np

import time
startTime = time.time()
games = [
    play_game(
        master = AutoMaster(solution=Solution.next_alldiff()),
        player = AutoPlayer(
            strategy=PosStrategy.optimize_positions,
            first_candidates=[isol(0,1,2,3),isol(2,3,4,5)]
        ),
        max_tours=20)
    for i in range(0, 250)]
endTime = time.time()

print("******************************************")
lengths = np.array([game.length() for game in games])
duration_ms = 1000 * (endTime - startTime)
print(f"duration: total={duration_ms :.0f}ms - avg={duration_ms // len(lengths) } ms")
print(f"mean:   {np.mean(lengths):.2f}")
print(f"median: {np.median(lengths)}")
print(f"min:    {np.min(lengths)}")
print(f"max:    {np.max(lengths)}")
print(f"std:    {np.std(lengths):.3f}")
