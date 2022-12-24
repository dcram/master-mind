from typing import List

from mastermind import ScoredCandidate, solution
from mastermind.constants import Color
from mastermind.position_solver import solve_positions, next_position_candidate
from mastermind.presence_solver import solve_presence, PresenceCandidate, next_presence_candidate

NUM_TOURS = 10

history = []

presence_solutions:List[PresenceCandidate] = solve_presence(history)
print(f'Num presence solutions: {len(presence_solutions)}')

TARGET = solution(Color.green, Color.blue, Color.red, Color.pink)
TARGET_PRESENCE_CANDIDATE = PresenceCandidate.from_solution(TARGET)
TARGET_PRESENCE_CANDIDATE_STR = TARGET_PRESENCE_CANDIDATE.to_s()

def show_psols(psols):
    for i, sol in enumerate(psols):
        target = ''
        if sol.to_s() == TARGET_PRESENCE_CANDIDATE:
            target = '******************* TARGET *************************'
        print('{:3d}. {} {}'.format(i, sol.to_s(), target))


for tour in range(0, NUM_TOURS):
    print("-"*80)
    print(f"Tour #{tour + 1}")
    sol_set = set([psol.to_s() for psol in presence_solutions])
    show_psols(presence_solutions)
    print(f'******* TARGET: {TARGET_PRESENCE_CANDIDATE_STR}')

    assert TARGET_PRESENCE_CANDIDATE_STR in sol_set

    if len(presence_solutions) == 1:
        print(f"FOUND COLORS!:  -> {presence_solutions[0]}")
        position_solutions = solve_positions(valid_presence=presence_solutions[0], history=history)
        print(f'Num position solutions: {len(position_solutions)}')
        if len(position_solutions) == 1:
            print(f"VICTORY !!!! -> {position_solutions[0]}")
            break
        else:
            candidate = next_position_candidate(candidates=position_solutions)
            print(f"Playing {candidate.to_s()}")
            scored_run = ScoredCandidate.compute(target=TARGET, candidate=candidate)
            history.append(scored_run)
    else:
        candidate = next_presence_candidate(candidates=presence_solutions)
        print(f"Playing {candidate.to_s()}")
        scored_run = ScoredCandidate.compute(target=TARGET, candidate=candidate)
        print(f"Score: {scored_run} ")
        history.append(scored_run)
        presence_solutions = solve_presence(history)
        print(f'Num presence solutions: {len(presence_solutions)}')
