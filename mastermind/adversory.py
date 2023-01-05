import random
from enum import Enum
from typing import List, Optional

from ortools.sat.python import cp_model

from mastermind import ScoredCandidate, Solution, Color
from mastermind.position_solver import next_position_candidate, solve_positions
from mastermind.presence_solver import PresenceCandidate, \
    ScoredPresenceCandidate, PresenceSolutionCallback


class Master():
    solution: Solution
    def score(self, candidate:Solution) -> Solution:
        pass

class AutoMaster(Master):
    def __init__(self, solution: Solution = Solution.random()):
        self.solution = solution
    def score(self, candidate:Solution) -> ScoredCandidate:
        return ScoredCandidate.compute(target=self.solution, candidate=candidate)

class HumanMaster(Master):
    def score(self, candidate:Solution) -> ScoredCandidate:
        print(f"Player plays {candidate}.")
        n_pres = int(input("Num presents? "))
        assert n_pres in range(0,5)
        n_pos = int(input("Num exacts? "))
        assert n_pos in range(0,5)
        return ScoredCandidate(candidate=candidate, num_presents = n_pres, num_exacts = n_pos)

class PosStrategy(Enum):
    random: int = 0
    optimize_positions: int = 1

class Player():
    def play(self, history:List[ScoredCandidate]) -> Solution:
        pass

def position_penalties(solution: Solution, solutions: List[Solution]) -> int:
    total_penalty = 0
    for i, color in enumerate(solution.colors()):
        num_at_position = len([existing for existing in solutions if existing.colors()[i] == color])
        penalty = 2 ** num_at_position - 1
        total_penalty += penalty
    return total_penalty


class AutoPlayer(Player):

    def __init__(self, strategy: PosStrategy, first_candidates: List[Solution] = []):
        self.presence_solutions = []
        self.position_solutions = []
        self.strategy = strategy
        self.first_candidates = first_candidates

    def play(self, history:List[ScoredCandidate]) -> Solution:
        presence_candidates = self.solve_presence(history)
        if len(presence_candidates) > 1:
            return self.next_presence_candidate(history = history, presence_candidates=presence_candidates, strategy=self.strategy)
        else:
            position_candidates = solve_positions(valid_presence=presence_candidates[0], history=history)
            return next_position_candidate(candidates=position_candidates)

    def next_presence_candidate(self, history:List[ScoredCandidate], presence_candidates: List[PresenceCandidate], strategy: PosStrategy) -> Solution:
        if len(history) < len(self.first_candidates):
            return self.first_candidates[len(history)]

        assert presence_candidates
        history_sols = [sc.candidate for sc in history]
        next_sol = random.choice(presence_candidates)
        colors = [cocc.color for cocc in next_sol.color_occs()]
        if strategy == PosStrategy.random:
            random.shuffle(colors)
            solution = Solution(color1=colors[0], color2=colors[1], color3=colors[2], color4=colors[3])
        elif strategy == PosStrategy.optimize_positions:
            from itertools import permutations
            best_permutation = None
            for p in permutations(colors):
                current_solution = Solution.from_colors(p)
                penalty = position_penalties(current_solution, solutions=history_sols)
                if not best_permutation:
                    best_permutation = p
                    best_penalty = penalty
                else:
                    if penalty < best_penalty:
                        best_permutation = p
                        best_penalty = penalty
            solution = Solution.from_colors(best_permutation)
        else:
            raise RuntimeError(f"Unknown strategy: {strategy}")
        return solution

    def solve_presence(self, history: List[ScoredCandidate]) -> List[PresenceCandidate]:

        hist: List[ScoredPresenceCandidate] = [ScoredPresenceCandidate.from_scored_candidate(scand) for scand in
                                               history]
        model = cp_model.CpModel()

        variables = {}
        for c in Color:
            for occ in range(0, 4):
                variables[(c, occ)] = model.NewIntVar(0, 1, f'color_{c.name}_{occ}')

        # Exactement quatre cases
        model.Add(sum(variables[c, occ] for c in Color for occ in range(0, 4)) == 4)

        for c in Color:
            # Si Vert1 est présent alors Vert0 aussi
            model.Add(variables[c, 0] >= variables[c, 1])
            # Si Vert2 est présent alors Vert1 aussi
            model.Add(variables[c, 1] >= variables[c, 2])
            # Si Vert3 est présent alors Vert2 aussi
            model.Add(variables[c, 2] >= variables[c, 3])

        for sol in hist:
            # num presents
            model.Add(sum(variables[c.color, c.occ] for c in sol.candidate.color_occs()) == sol.num_ok)

        solver = cp_model.CpSolver()
        solution_callback = PresenceSolutionCallback(variables)
        solver.parameters.enumerate_all_solutions = True

        solver.Solve(model, solution_callback)

        return solution_callback.solutions
