from mastermind.adversory import AutoMaster, AutoPlayer, HumanMaster

NUM_TOURS = 10

master = AutoMaster()
player = AutoPlayer()

history = []
wins = False
num_tours = -1
for tour in range(0, NUM_TOURS):
    print("-"*80)
    print(f"Tour #{tour + 1}")
    candidate = player.play(history=history)
    scored_candidate = master.score(candidate=candidate)
    history.append(scored_candidate)
    if scored_candidate.num_exacts == 4:
        wins = True
        num_tours = tour + 1
        break


print("******************************************")
for i, sc in enumerate(history):
    print('{:3d}. {:8s} {:8s} {:8s} {:8s} {} {}'.format(
        1+i,
        sc.candidate.color1.name,
        sc.candidate.color2.name,
        sc.candidate.color3.name,
        sc.candidate.color4.name,
        sc.num_presents, sc.num_exacts))
print("******************************************")
if wins:
    print(f"Player wins in {num_tours} tours !!")
else:
    print(f"Player loses")