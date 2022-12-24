from typing import List

from ortools.sat.python import cp_model

from mastermind import Solution, ScoredCandidate
from mastermind.constants import Color
from mastermind.presence_solver import PresenceCandidate


class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, valid_presence: PresenceCandidate, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.valid_presence = valid_presence
        self.__variables = variables
        self.solutions = []
        self.__solution_count = 0

    def find_color_at_case(self, case: int) -> Color:
        for color in self.valid_presence.color_groups().keys():
            if self.Value(self.__variables[case, color]):
                return color
        raise f"No color at case {case + 1}"

    def on_solution_callback(self):
        self.__solution_count += 1
        self.solutions.append(Solution(
            color1 = self.find_color_at_case(0),
            color2 = self.find_color_at_case(1),
            color3 = self.find_color_at_case(2),
            color4 = self.find_color_at_case(3)))

    def solution_count(self):
        return self.__solution_count

import random

def next_position_candidate(candidates: List[Solution]) -> Solution:
    assert candidates
    next_sol = random.choice(candidates)
    return next_sol

def solve_positions(valid_presence: PresenceCandidate, history: List[ScoredCandidate]) -> List[Solution]:
    model = cp_model.CpModel()

    variables = {}
    for case in range(0, 4):
        for color in valid_presence.color_groups().keys():
            variables[case, color] = model.NewBoolVar(f'case_{case+1}_color_{color.name}')

    # Exactement quatre cases
    model.Add(sum(variables[case, color] for case in range(0, 4) for color in valid_presence.color_groups().keys()) == 4)

    # Exactement une couleur par case
    for case in range(0,4):
        model.AddExactlyOne(variables[case, color]  for color in valid_presence.color_groups().keys())

    # Num of occurrences for each color
    for color, occs in valid_presence.color_groups().items():
        model.Add(sum(variables[case, color] for case in range(0,4)) == len(occs))

    # Scoring history
    for score_cand in history:
        # num_exacts
        cand_variables = []
        for case in range(0,4):
            candidate_color = score_cand.candidate.colors()[case]
            if candidate_color in valid_presence.color_groups():
                cand_variables.append(variables[case, candidate_color])
        model.Add(sum(cand_variables) == score_cand.num_exacts)

    solver = cp_model.CpSolver()
    solution_callback = SolutionCallback(valid_presence, variables)
    solver.parameters.enumerate_all_solutions = True

    solver.Solve(model, solution_callback)

    return solution_callback.solutions
