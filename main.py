from mastermind import sol, Solution
from mastermind.adversory import AutoMaster, AutoPlayer, PosStrategy
from mastermind.game import play_game

game = play_game(master = AutoMaster(solution=Solution.next_alldiff()), player = AutoPlayer(strategy=PosStrategy.optimize_positions))

print("******************************************")
for i, sc in enumerate(game.history):
    print('{:3d}. {:8s} {:8s} {:8s} {:8s} {} {}'.format(
        1+i,
        sc.candidate.color1.name,
        sc.candidate.color2.name,
        sc.candidate.color3.name,
        sc.candidate.color4.name,
        sc.num_presents, sc.num_exacts))
print("******************************************")
if game.wins():
    print(f"Player wins in {len(game.history)} tours !!")
else:
    print(f"Player loses")