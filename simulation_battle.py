import numpy as np
import random
import json
import math
import operator

from creature import Creature
from bullet import Bullet

from pygame.math import Vector2

from helpers import check_collision
from helpers import calculateLOS
from helpers import constrainAngle

from movement import advanceAntiClockwise, advanceClockwise, rotateAntiClockwise, rotateClockwise, shoot, moveStraight, wrap, constrainBounds

#import matplotlib.pyplot as plt
#from matplotlib import style

class Simulation():

	def __init__(self, weights_path = None):
		with open("config.json") as cfg:
			config = json.load(cfg)

		self.population_size = config['population_size']
		self.creature_vision_range = config['creature_vision_range']
		self.bullet_vision_range = config['bullet_vision_range']
		self.rotation_speed = config['rotation_speed']
		self.child_size = config['child_size']
		self.lucky_few = config['lucky_few']
		self.best_few = config['best_few']
		self.creature_speed = config['creature_speed']
		self.creature_radius = config['creature_radius']
		self.bullet_radius = config['bullet_radius']

		config = None

		#Create initial population
		self.creatures = []

		if weights_path == None:
			for i in range(self.population_size):
				self.creatures.append(Creature())

		else:
			with open(weights_path) as infile:
				weights = json.load(infile)

			infile = None

			for i in range(len(weights)):
				self.creatures.append(Creature(np.array(weights[i]['syn0']), np.array(weights[i]['syn1']), np.array(weights[i]['syn2'])))

	def mutate(self, element):
		#Select mutation for element
		chance = random.randint(0, 3)
		if chance == 0:
			return element * (random.random() + 0.5)
		elif chance == 1:
			return -element
		elif chance == 2:
			return 2*random.random() - 1
		else:
			if random.random() * 100 < 50:
				return element + (random.random())
			else:
				return element - (random.random())

	def mutateCreature(self, creature):
		
		random_value = np.random.uniform(-1.0, 1.0, 1)

		#Mutate syn0
		for x in np.nditer(creature.syn0, op_flags=['readwrite']):
			if random.random() * 100 <= creature.mutationChance:
				x[...] = x[...] * random_value

		#Mutate syn1
		for x in np.nditer(creature.syn1, op_flags=['readwrite']):
			if random.random() * 100 <= creature.mutationChance:
				x[...] = x[...] * random_value

		#Mutate syn2
		for x in np.nditer(creature.syn2, op_flags=['readwrite']):
			if random.random() * 100 <= creature.mutationChance:
				x[...] = x[...] * random_value

		return creature

	def mutatePopulation(self, creatures):
		mutatedPopulation = []
		for creature in creatures:
			mutatedPopulation.append(self.mutateCreature(creature))
		return mutatedPopulation

	def createChild(self, creature1, creature2):

		#Create child syn0
		syn0 = np.zeros((4,5))
		for index, x in np.ndenumerate(syn0):
			if random.random() * 100 < 50:
				syn0[index] = creature1.syn0[index]
			else:
				syn0[index] = creature2.syn0[index]
			
		#Create child syn1
		syn1 = np.zeros((6,5))
		for index, x in np.ndenumerate(syn1):
			if random.random() * 100 < 50:
				syn1[index] = creature1.syn1[index]
			else:
				syn1[index] = creature2.syn1[index]

		#Create child syn2
		syn2 = np.zeros((6,5))
		for index, x in np.ndenumerate(syn2):
			if random.random() * 100 < 50:
				syn2[index] = creature1.syn2[index]
			else:
				syn2[index] = creature2.syn2[index]

		return Creature(syn0, syn1, syn2)

	def get_average_fitness(self):
		total = 0
		for creature in self.creatures:
			total += creature.fitness

		return total/len(self.creatures)

	def get_top_two(self):
		#Returns top two creatures for 1v1

		return self.best_creature, self.second_best


	def get_best(self):
		#Get returns best fitness
		max_fitness = None
		for creature in self.creatures:

			if max_fitness == None:
				max_fitness = creature.fitness
				best_creature = creature

			elif creature.fitness > max_fitness:
				max_fitness = creature.fitness
				best_creature = creature
		print(best_creature.history)		
		return max_fitness

	def createParents(self, population):
		#Create parents of best fitness and lucky few
		parents = []

		#Calculate best few
		perf_population = {}
		for individual in population:
			perf_population[individual] = individual.fitness

		perf_population = sorted(perf_population.items(), key=operator.itemgetter(1), reverse=True)
		for i in range(self.best_few):
			parents.append(perf_population[i][0])

		for i in range(self.lucky_few):
			parents.append(random.choice(population))

		self.best_creature = perf_population[0][0]
		self.second_best = perf_population[1][0]

		random.shuffle(parents)
		return parents

	def createChildren(self, breeders):
		#Create children of next generation
		nextPopulation = []
		for i in range(len(breeders)//2):
			for j in range(self.child_size):
				nextPopulation.append(self.createChild(breeders[i],breeders[len(breeders)-1-i]))

		return nextPopulation

	def nextGeneration(self):
		#Create next generation of creatures
		parents = self.createParents(self.creatures)
		self.creatures = self.mutatePopulation(self.createChildren(parents))

		#Keep best creature from last generation
		best_creature = Creature(self.best_creature.syn0, self.best_creature.syn1, self.best_creature.syn2)
		best_creature.name = 'PreviousBest'
		self.creatures.append(best_creature)
		#Mutate a new best creature
		mutated_best = Creature(self.best_creature.syn0, self.best_creature.syn1, self.best_creature.syn2)
		mutated_best.name = 'MutatedBest'
		self.creatures.append(self.mutateCreature(mutated_best))


	def check_los(self, target_creature, creature, vision_range):

		delta_x = abs(target_creature.x - creature.x)
		delta_y = abs(target_creature.y - creature.y)

		if delta_x == 0 and delta_y == 0:
			#Creatures are right on top of each other
			return 0

		elif delta_x == 0 and target_creature.y > creature.y:
			return calculateLOS(target_creature, delta_x, delta_y, vision_range, 5)

		elif delta_x == 0 and target_creature.y < creature.y:
			return calculateLOS(target_creature, delta_x, delta_y, vision_range, 6)

		elif target_creature.x > creature.x and delta_y == 0:
			return calculateLOS(target_creature, delta_x, delta_y, vision_range, 7)

		elif target_creature.x < creature.x and delta_y == 0:
			return calculateLOS(target_creature, delta_x, delta_y, vision_range, 8)

		elif target_creature.x > creature.x and target_creature.y > creature.y: #Top Left
			return calculateLOS(target_creature, delta_x, delta_y, vision_range, 1)

		elif target_creature.x > creature.x and target_creature.y < creature.y: #Bottom Left		
			return calculateLOS(target_creature, delta_x, delta_y, vision_range, 2)

		elif target_creature.x < creature.x and target_creature.y < creature.y: #Bottom Right		
			return calculateLOS(target_creature, delta_x, delta_y, vision_range, 3)

		else: #Top Right
			return calculateLOS(target_creature, delta_x, delta_y, vision_range, 4)

	def get_inputs(self, target_creature, competitors):
		#Gets the inputs based on the surroundings of the creature
		LOS = 0
		enemy_ball = 0
		ball_fired = 0
		#0-Enemy in LOS 1-Enemy Ball in LOS 2-Ball Fired

		#Returns 0 if nothing in LOS. Returns pythagorean distance to object if there is
		for creature in competitors:
			if creature != target_creature:
				LOS = self.check_los(target_creature, creature, self.creature_vision_range)
				if LOS != 0:
					LOS = 1 - (LOS/target_creature.width)
					#target_creature.tracking += .05
					#target_creature.fitness += target_creature.tracking
				else:
					target_creature.tracking = 0
				break

		for creature in competitors:
			bullet_angle = 0
			if not creature.can_shoot and creature != target_creature:
				enemy_ball = self.check_los(target_creature, creature.bullet, self.bullet_vision_range)
				if enemy_ball != 0:
					enemy_ball = 1 - (enemy_ball/target_creature.width)
				break

		if not target_creature.can_shoot:
			ball_fired = 1
		
		target_creature.inputs = (LOS, enemy_ball, ball_fired)
		#print(LOS, enemy_ball, ball_fired)
		return (int(bool(LOS)), int(bool(enemy_ball)), ball_fired)

	def step(self, competitors):
		#Runs every frame of the simulation. 

		#Update creatures and bullets
		for creature in competitors:
			#Make sure that creature is alive
			if creature.is_alive:
				#Check if bullets have gone out of bounds
				if not creature.can_shoot and creature.bullet.update():
					creature.bullet = None
					creature.can_shoot = True

					#Discourage missing
					#creature.fitness -= 2

				#If creature is alive, add 0.1 to fitness. The longer it survives, the better
				#creature.fitness += 0.1

				#If creature is not moving, -0.2 from fitness. Trying to encourage creatures to move.
				#if not creature.moving:
					#creature.fitness -= 0.1

				#Detect collision with bullet
				for _creature in competitors:
					if not _creature.can_shoot and _creature.is_alive and _creature != creature:
						if check_collision(creature, self.creature_radius, _creature.bullet, self.bullet_radius):
							#If there is a collision, reward and deduct fitness accordingly
							_creature.hit_target()
							_creature.bullet = None
							_creature.can_shoot = True
							creature.get_hit()

				#Get creature decision
				initial_rotation = creature.rotation
				inputs = self.get_inputs(creature, competitors)
				choice = creature.update(inputs[0], inputs[1], inputs[2])
				#print(choice)

			#Does a move based on the creature's choice
			#0-Move Forward and Anti-Clockwise 1-Move Forward and Clockwise 2-Turn anti-clockwise 3-Turn clockwise 4-Shoot
				if choice == 0:
					advanceAntiClockwise(creature, self.creature_speed, 3)
					#moveStraight(creature, self.creature_speed)
				elif choice == 1:
					advanceClockwise(creature, self.creature_speed, 3)
					#moveStraight(creature, -self.creature_speed)

				elif choice == 2:
					#rotateAntiClockwise(creature, self.rotation_speed)
					advanceAntiClockwise(creature, self.creature_speed+5, 20)

				elif choice == 3:
					#rotateClockwise(creature, self.rotation_speed)
					advanceClockwise(creature, self.creature_speed+5, 20)		

				else:

					if creature.can_shoot:
						shoot(creature)
						#creature.fitness += 10

					else:
						#creature.fitness -= 1
						advanceAntiClockwise(creature, self.creature_speed, 5)
						
				
				#Wrap around
				#wrap(creature, self.creature_radius)

				#Constrain creatures to bounds
				constrainBounds(creature, self.creature_radius, creature.bounds, creature.width)

				#Update inputs after moving for visual purposes
				self.get_inputs(creature, competitors)

if __name__ == '__main__':
	test = Simulation()
	generation_history = []
	generation_ave = []
	for _ in range(20):
		for i in range(20):
			test.step()
		temp = test.get_best()
		generation_history.append(temp)
		generation_ave.append(test.get_average_fitness())
		print(f'Best of generation: {temp}')
		test.nextGeneration()



	plt.plot([x for x in range(20)],generation_ave,'b')
	plt.plot([x for x in range(20)],generation_history,'r')
	plt.show()
