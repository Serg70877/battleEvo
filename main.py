import pygame

from gui_battle import GUI

game = GUI('weights.json')

while game.is_running:
	if game.test_mode:
		game.testLoop()
		game.draw()
		game.handleTestEvents()
		
	else:
		if not game.battle_mode:
			game.roundRobinLoop()
		else:
			game.battleLoop()

		if not game.FAST_FORWARD:
			game.draw()
		game.handleEvents()

pygame.quit()