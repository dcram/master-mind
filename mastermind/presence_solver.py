from typing import List

from ortools.sat.python import cp_model
from pydantic import BaseModel

from mastermind import ScoredCandidate, ColorOcc, Color, Solution


class PresenceCandidate(BaseModel):
    color1: ColorOcc
    color2: ColorOcc
    color3: ColorOcc
    color4: ColorOcc

    def color_occs(self):
        return [self.color1, self.color2, self.color3, self.color4]

    def to_s(self):
        return " ".join(f'{c.color.name}_{c.occ+1}' for c in self.color_occs())

    def score(self, actual_solution:"PresenceCandidate") -> "ScoredPresenceCandidate":
        actual_color_occs = actual_solution.color_occs()
        return sum(1 for cocc in self.color_occs() if cocc in actual_color_occs)

    def color_groups(self) -> dict[Color, List[ColorOcc]]:
        g = {}
        for idx, cocc in enumerate(self.color_occs()):
            if cocc.color not in g:
                g[cocc.color] = []
            g[cocc.color].append(idx)
        return g

    @staticmethod
    def from_solution(solution: Solution):
        return PresenceCandidate.from_colors(solution.colors())

    @staticmethod
    def from_colors(colors: List[Color]):
        color_occ_index = {}
        color_occs = []
        for c in sorted(colors, key=lambda x: x.value):
            if c not in color_occ_index:
                color_occ_index[c] = 0
            else:
                color_occ_index[c] += 1
            color_occs.append(ColorOcc(color=c, occ=color_occ_index[c]))
        return PresenceCandidate(color1 = color_occs[0], color2 = color_occs[1], color3 = color_occs[2], color4 = color_occs[3])


class ScoredPresenceCandidate(BaseModel):
    candidate: PresenceCandidate
    num_ok: int

    @staticmethod
    def from_scored_candidate(scored_cand: ScoredCandidate) -> "ScoredPresenceCandidate":
        return ScoredPresenceCandidate(
            candidate = PresenceCandidate.from_solution(scored_cand.candidate),
            num_ok = scored_cand.num_presents
        )


class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.solutions = []
        self.__solution_count = 0

    def as_candidate(self) -> PresenceCandidate:
        color_occs = []
        for c in Color:
            for occ in range(0,4):
                if self.Value(self.__variables[c, occ]):
                    color_occs.append(ColorOcc(color=c, occ=occ))
        return PresenceCandidate(color1 = color_occs[0], color2 = color_occs[1], color3 = color_occs[2], color4 = color_occs[3])

    def on_solution_callback(self):
        self.__solution_count += 1
        self.solutions.append(self.as_candidate())

    def solution_count(self):
        return self.__solution_count

import random

def next_presence_candidate(candidates: List[PresenceCandidate]) -> Solution:
    assert candidates
    next_sol = random.choice(candidates)
    colors = [cocc.color for cocc in next_sol.color_occs()]
    random.shuffle(colors)
    solution = Solution(color1=colors[0], color2=colors[1], color3=colors[2], color4=colors[3])
    return solution


def solve_presence(history: List[ScoredCandidate]) -> List[PresenceCandidate]:

    hist: List[ScoredPresenceCandidate] = [ScoredPresenceCandidate.from_scored_candidate(scand) for scand in history]
    model = cp_model.CpModel()

    variables = {}
    for c in Color:
        for occ in range(0,4):
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
    solution_callback = SolutionCallback(variables)
    solver.parameters.enumerate_all_solutions = True

    solver.Solve(model, solution_callback)

    return solution_callback.solutions
