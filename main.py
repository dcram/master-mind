from mastermind.adversory import AutoMaster, AutoPlayer

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
    print(f"Player plays {candidate}")
    scored_candidate = master.score(candidate=candidate)
    print(f"Score: {scored_candidate}")
    if scored_candidate.num_exacts == 4:
        wins = True
        num_tours = tour + 1
        break
    else:
        history.append(scored_candidate)

print("******************************************")
if wins:
    print(f"Player wins in {num_tours} tours !!")
else:
    print(f"Player loses")