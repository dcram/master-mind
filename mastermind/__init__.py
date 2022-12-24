from typing import List

from pydantic import BaseModel

from mastermind.constants import Color


class ColorOcc(BaseModel):
    color: Color
    occ: int

    def __str__(self):
        return f'{self.color.name}_{self.occ}'


class Solution(BaseModel):
    color1: Color
    color2: Color
    color3: Color
    color4: Color

    def __str__(self):
        return self.to_s()

    def to_s(self):
        return " ".join(c.name for c in self.colors())

    def colors(self):
        return [self.color1,self.color2,self.color3,self.color4]

    def as_colors_occs(self) -> List[ColorOcc]:
        l = []
        for c in Color:
            occ = 0
            for solcolor in self.colors():
                if c == solcolor:
                    l.append(ColorOcc(color=c, occ=occ))
                    occ += 1
        return l

    def distinct_colors(self):
        return set(self.colors())

    def color_indices(self):
        return [c.value for c in self.colors()]

    @staticmethod
    def random():
        return Solution(
            color1=Color.random(),
            color2=Color.random(),
            color3=Color.random(),
            color4=Color.random()
        )

class ScoredCandidate(BaseModel):
    candidate: Solution
    num_presents: int
    num_exacts: int

    def __str__(self):
        return f'{self.candidate} [pres: {self.num_presents}, pos: {self.num_exacts}]'

    @staticmethod
    def compute(target:Solution, candidate: Solution):
        return ScoredCandidate(
            candidate=candidate,
            num_presents=num_presents(target=target, candidate=candidate),
            num_exacts=num_exacts(target=target, suggestion=candidate),
        )


def solution(color1, color2, color3, color4):
    return Solution(color1=color1, color2=color2, color3=color3, color4=color4)


def num_exacts(target: Solution, suggestion: Solution) -> int:
    return sum([1 for c1, c2 in zip(target.colors(), suggestion.colors()) if c1 == c2])

def num_presents(target: Solution, candidate: Solution) -> int:
    presents = []
    s_colors = candidate.colors()
    t_colors = target.colors()
    for c in s_colors:
        if c in t_colors:
            t_colors.remove(c)
            presents.append(c)
    return len(presents)

