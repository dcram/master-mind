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


class PresenceSolutionCallback(cp_model.CpSolverSolutionCallback):
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




