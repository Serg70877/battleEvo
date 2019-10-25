import pygame
import json
import numpy as np

from simulation_battle import Simulation
from helpers import gameIterator
from creature import Creature
from movement import advanceAntiClockwise, advanceClockwise, rotateAntiClockwise, rotateClockwise, shoot, moveStraight, wrap, constrainBounds

from pygame.math import Vector2

class GUI:
	#Handles GUI and loops
	def __init__(self, path_name = None):
		with open("config.json") as cfg:
			config = json.load(cfg)

		self.SCREEN_WIDTH = config['width']
		self.SCREEN_HEIGHT = config['height']
		self.creature_radius = config['creature_radius']
		self.bullet_radius = config['bullet_radius']
		self.population_size = config['population_size']
		self.fast_forward_frames = config['fast_forward_frames']

		config = None

		#Debugging
		self.test_mode = False

		self.FAST_FORWARD = False
		self.autoplay = True
		self.update_display = True

		self.COLOUR_KEY = (255,255,255)

		self.is_running = True

		#Set up pygame stuff
		pygame.init()

		self.DISPLAYSURF = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)

		self.FPS = 30 #Frames per second
		self.fpsClock = pygame.time.Clock()

		#Cache images
		self.creature_image = pygame.Surface((self.creature_radius*2, self.creature_radius*2))
		self.creature_image.fill((255,255,255))
		pygame.draw.circle(self.creature_image, (255,0,0), (self.creature_radius, self.creature_radius), self.creature_radius, 1)
		self.creature_image.set_colorkey(self.COLOUR_KEY)

		self.bullet_image = pygame.Surface((self.bullet_radius*2, self.bullet_radius*2))
		self.bullet_image.fill((255,255,255))
		pygame.draw.circle(self.bullet_image, (0,0,0), (self.bullet_radius, self.bullet_radius), self.bullet_radius, 1)
		self.bullet_image.set_colorkey(self.COLOUR_KEY)

		self.eye_image = pygame.Surface((self.bullet_radius*2, self.bullet_radius*2))
		self.eye_image.fill((255,255,255))
		pygame.draw.circle(self.eye_image, (0,0,0), (self.bullet_radius, self.bullet_radius), self.bullet_radius, 0)
		self.eye_image.set_colorkey((self.COLOUR_KEY))

		#Debugging images
		#Green - Enemy Detected
		self.eye_enemy = pygame.Surface((self.bullet_radius*2, self.bullet_radius*2))
		self.eye_enemy.fill((255,255,255))
		pygame.draw.circle(self.eye_enemy, (0,255,0), (self.bullet_radius, self.bullet_radius), self.bullet_radius, 0)
		self.eye_enemy.set_colorkey((self.COLOUR_KEY))

		#Blue - Bullet Detected
		self.eye_bullet = pygame.Surface((self.bullet_radius*2, self.bullet_radius*2))
		self.eye_bullet.fill((255,255,255))
		pygame.draw.circle(self.eye_bullet, (0,0,255), (self.bullet_radius, self.bullet_radius), self.bullet_radius, 0)
		self.eye_bullet.set_colorkey((self.COLOUR_KEY))

		#Purple - Both Enemy and Bullet Detected
		self.eye_both = pygame.Surface((self.bullet_radius*2, self.bullet_radius*2))
		self.eye_both.fill((255,255,255))
		pygame.draw.circle(self.eye_both, (255,0,255), (self.bullet_radius, self.bullet_radius), self.bullet_radius, 0)
		self.eye_both.set_colorkey((self.COLOUR_KEY))

		#Middle line
		self.line = pygame.Surface((1, self.SCREEN_HEIGHT))
		self.line.fill((0,0,0))

		self.DISPLAYSURF.fill((255,255,255))

		#Set up simulation
		if path_name == None:
			self.simulation = Simulation()
		elif path_name == 'test':
			self.simulation = Simulation()
			self.simulation.creatures = (Creature(), Creature())
			self.test_mode = True
		else:
			self.simulation = Simulation(path_name)
		self.counter = 0
		self.game = gameIterator(self.simulation.creatures)
		self.next_match = True
		self.battle_mode = False
		

		#Text counters
		self.current_generation = 0
		self.match_number = 1

		#Fonts
		self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
		self.score_font = pygame.font.SysFont('Calibri', 40)

		#Check if battle mode or normal round robin
		if len(self.simulation.creatures) == 2:
			self.battle_mode = True
			self.competitors = self.simulation.creatures

			for n,competitor in enumerate(self.competitors):
					competitor.bounds = n
					competitor.reset(competitor.bounds)

	def testLoop(self):
		for creature in self.competitors:
			self.simulation.get_inputs(creature, self.competitors)

	def battleLoop(self):
		#Mainloop for 1v1
		for creature in self.competitors:
			if not creature.is_alive:
				previous_fitness = creature.fitness
				creature.reset(creature.bounds)
				creature.fitness = previous_fitness
		if self.autoplay:
			if self.FAST_FORWARD:
				for i in range(10):
					self.simulation.step(self.competitors)
			else:
				self.simulation.step(self.competitors)


	def roundRobinLoop(self):
		#Normal Mainloop used for training
		if self.next_match:
			if self.match_number == self.population_size**2 - self.population_size + 1:
				self.simulation.nextGeneration()
				self.current_generation += 1
				self.game = gameIterator(self.simulation.creatures)
				self.competitors = self.game.__next__()
				self.next_match = False
				self.match_number = 1

				#Reset competitors health
				for n,competitor in enumerate(self.competitors):
					competitor.bounds = n
					competitor.reset(competitor.bounds)

			else: 
				self.competitors = self.game.__next__()
				#Ensure that creatures cannot be matched against themselves
				if self.competitors == None:
					self.competitors = self.game.__next__()
				self.next_match = False

				#Reset competitors health
				for n,competitor in enumerate(self.competitors):
					competitor.bounds = n
					competitor.reset(competitor.bounds)

			#Update simulation
		if self.FAST_FORWARD:
			for i in range(self.fast_forward_frames):
				self.simulation.step(self.competitors)
				self.counter += 1
		else:
			self.simulation.step(self.competitors)
			self.counter += 1

		if self.counter >= 600 or not self.competitors[0].is_alive or not self.competitors[1].is_alive:

			self.counter = 0
			self.next_match = True
			self.match_number += 1

	def draw(self):
		#Drawing method
		self.DISPLAYSURF.fill((255,255,255))

		#Draw Text
		generation_text = self.myfont.render(f'Curent Generation: {self.current_generation}', False, (0, 0, 0))
		self.DISPLAYSURF.blit(generation_text, (10,0))

		current_match = self.myfont.render(f'Match {self.match_number}', False, (0, 0, 0))
		self.DISPLAYSURF.blit(current_match, (self.SCREEN_WIDTH/2+10+50,0))

		competitor1_points = self.score_font.render(f'{self.competitors[0].name}: {int(self.competitors[0].fitness)}', False, (0, 0, 0))
		competitor2_points = self.score_font.render(f'{self.competitors[1].name}: {int(self.competitors[1].fitness)}', False, (0, 0, 0))
		self.DISPLAYSURF.blit(competitor1_points, (10,50))
		self.DISPLAYSURF.blit(competitor2_points, (self.SCREEN_WIDTH/2+10+50,50))

		#Draw line
		self.DISPLAYSURF.blit(self.line, (self.SCREEN_WIDTH/2 + 50, 0))
		self.DISPLAYSURF.blit(self.line, (self.SCREEN_WIDTH/2 - 50, 0))

		#Draw creatures and bullets
		for creature in self.competitors:
			if creature.is_alive:
				#Draw creature
				self.DISPLAYSURF.blit(self.creature_image, (creature.x - self.creature_radius, creature.y - self.creature_radius))
				
				#Find creature's eye position and draw creature's eye
				eye_pos = Vector2(0, self.creature_radius).rotate(creature.rotation)
				#Find what colour eye to draw
				if creature.inputs != None:
					if creature.inputs[0] != 0 and creature.inputs[1] != 0:
						eye = self.eye_both
					elif creature.inputs[0] != 0:
						eye = self.eye_enemy
					elif creature.inputs[1] != 0:
						eye = self.eye_bullet
					else:
						eye = self.eye_image
				else:
					eye = self.eye_image
				self.DISPLAYSURF.blit(eye, (creature.x + eye_pos[0] - self.bullet_radius, creature.y - eye_pos[1] - self.bullet_radius))
				
				if not creature.can_shoot:
					#Draw bullet
					self.DISPLAYSURF.blit(self.bullet_image,(creature.bullet.x - self.bullet_radius, creature.bullet.y - self.bullet_radius))

		#Clock stuff
		self.fpsClock.tick(self.FPS)
		#print(fpsClock.get_fps())

		#Turn off display updating for performance
		if self.update_display:
			pygame.display.update()

	def handleEvents(self):
		for event in pygame.event.get():

			#Quit pygame if ESC is pressed
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):

				self.is_running = False

			elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:

				self.FAST_FORWARD = not self.FAST_FORWARD

			elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:

				self.autoplay = not self.autoplay

			elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:

				if not self.autoplay:
					self.simulation.step(self.competitors)

			elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:

				for competitor in self.competitors:
					print(competitor.inputs)

			elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:

				self.update_display = not self.update_display

			elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				if not self.battle_mode:
					#Save population
					with open('weights.json', 'w') as outfile:
						weights = []
						for creature in self.simulation.creatures:
							weights.append({
											"syn0" : np.ndarray.tolist(creature.syn0),
											"syn1" : np.ndarray.tolist(creature.syn1),
											"syn2" : np.ndarray.tolist(creature.syn2)
							})

						json.dump(weights, outfile)
							
					print('Saved!')
				else:
					#Reset creature positions
					for n,creature in enumerate(self.competitors):
						previous_fitness = creature.fitness
						creature.reset(n)
						creature.fitness = previous_fitness

			elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
				with open('specificCreatureWeights.json', 'w') as outfile:
					weights = []
					for creature in self.competitors:
						weights.append({
										"syn0" : np.ndarray.tolist(creature.syn0),
										"syn1" : np.ndarray.tolist(creature.syn1),
										"syn2" : np.ndarray.tolist(creature.syn2)
						})

					json.dump(weights, outfile)

				print('Creature Saved!')

			elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSLASH:
				with open('topTwoWeights.json', 'w') as outfile:
					weights = []
					for creature in self.simulation.get_top_two():
						weights.append({
										"syn0" : np.ndarray.tolist(creature.syn0),
										"syn1" : np.ndarray.tolist(creature.syn1),
										"syn2" : np.ndarray.tolist(creature.syn2)
						})

					json.dump(weights, outfile)

				print('Top 2 creatures Saved!')

		
	def handleTestEvents(self):
		for event in pygame.event.get():

			#Quit pygame if ESC is pressed
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):

				self.is_running = False

		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP]:
			moveStraight(self.competitors[0], self.simulation.creature_speed)
		elif keys[pygame.K_DOWN]:
			moveStraight(self.competitors[0], -self.simulation.creature_speed)
		elif keys[pygame.K_RIGHT]:
			advanceClockwise(self.competitors[0], self.simulation.creature_speed, 15)		
		elif keys[pygame.K_LEFT]:
			advanceAntiClockwise(self.competitors[0], self.simulation.creature_speed, 15)
		elif keys[pygame.K_SPACE]:
			shoot(self.competitors[0])


			