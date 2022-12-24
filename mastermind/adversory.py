from typing import List

from pydantic import BaseModel

from mastermind import ScoredCandidate, Solution
from mastermind.position_solver import next_position_candidate, solve_positions
from mastermind.presence_solver import solve_presence, next_presence_candidate


class Master():
    def score(self, candidate:Solution) -> Solution:
        pass

class AutoMaster(Master):
    def __init__(self):
        self.target = Solution.random()
    def score(self, candidate:Solution) -> ScoredCandidate:
        return ScoredCandidate.compute(target=self.target, candidate=candidate)

class HumanMaster(Master):
    def score(self, candidate:Solution) -> ScoredCandidate:
        print(f"Player plays {candidate}.")
        n_pres = int(input("Num presents? "))
        assert n_pres in range(0,5)
        n_pos = int(input("Num exacts? "))
        assert n_pos in range(0,5)
        return ScoredCandidate(candidate=candidate, num_presents = n_pres, num_exacts = n_pos)

class Player():
    def play(self, history:List[ScoredCandidate]) -> Solution:
        pass

class AutoPlayer(Player):

    def __init__(self):
        self.presence_solutions = []
        self.position_solutions = []

    def play(self, history:List[ScoredCandidate]) -> Solution:
        presence_candidates = solve_presence(history)
        if len(presence_candidates) > 1:
            return next_presence_candidate(candidates=presence_candidates)
        else:
            position_candidates = solve_positions(valid_presence=presence_candidates[0], history=history)
            return next_position_candidate(candidates=position_candidates)
