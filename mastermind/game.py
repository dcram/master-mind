from typing import List

from pydantic import BaseModel

from mastermind import ScoredCandidate, Solution
from mastermind.adversory import Player, Master

DEFAULT_MAX_TOURS = 10


class Game(BaseModel):
    solution: Solution
    history: List[ScoredCandidate]

    def length(self) -> int:
        return len(self.history)

    def wins(self) -> bool:
        return self.solution == self.history[-1].candidate

def play_game(master: Master, player:Player, max_tours: int = DEFAULT_MAX_TOURS, verbose:str = False) -> Game:
    history = []
    wins = False
    for tour in range(0, max_tours):
        if verbose:
            print("-" * 80)
            print(f"Tour #{tour + 1}")
        candidate = player.play(history=history)
        scored_candidate = master.score(candidate=candidate)
        history.append(scored_candidate)
        if scored_candidate.num_exacts == 4:
            wins = True
            break
    game = Game(solution=master.solution, history=history)
    assert game.wins() == wins
    return game
