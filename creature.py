import json
import random
import numpy as np
import scipy.special

from bullet import Bullet

def sigmoid(x):
	return scipy.special.expit(x)

def softmax(x):
    return np.exp(x) / float(sum(np.exp(x)))

class Creature():

	def __init__(self, syn0=None, syn1=None, syn2=None):
		with open("config.json") as cfg:
			config = json.load(cfg)

		self.width = config['width']
		self.height = config['height']
		self.mutationChance = config['mutationChance'] #(1/(np.size(self.syn0) + np.size(self.syn1))) * 200

		self.name = random.choice(config['names']) #chr(random.randint(65,122))

		#Where the creature is bounded to. 0 means left half, 1 means right half
		self.bounds = None

		config = None

		#Position and rotation info
		self.x = random.randint(0, self.width)
		self.y = random.randint(0, self.height)
		self.rotation = random.randint(0, 360)
		self.can_shoot = True
		self.bullet = None

		self.inputs = None

		#Life and stuff
		self.health = 3
		self.is_alive = True

		self.tracking = 0
		self.fitness = 0
		self.moving = False

		#For debugging
		self.history = []

		if type(syn0) == type(None) and type(syn1) == type(None):
			#Synapse Layer 1 | 3 inputs + 1 bias 5 outputs (Sigmoid)
			self.syn0 = 2*np.random.random((4,5)) - 1

			#Synapse Layer 2 | 5 inputs + 1 bias 5 outputs (Sigmoid)
			self.syn1 = 2*np.random.random((6,5)) - 1

			#Synapse Layer 3 | 5 inputs + 1 bias 5 outputs (Softmax)
			self.syn2 = 2*np.random.random((6,5)) - 1
		else:
			self.syn0 = syn0
			self.syn1 = syn1
			self.syn2 = syn2

	def reset(self, bounds):
		self.health = 3
		self.is_alive = True
		self.bullet = None
		self.can_shoot = True
		self.y = random.randint(0, self.height)
		self.rotation = random.randint(0, 360)

		#Set creature X to left half if bounds = 0 and right half if bounds = 1
		if bounds == 0:
			self.x = random.randint(0, self.width/2)
		elif bounds == 1:
			self.x = random.randint(self.width/2, self.width)
		else:
			bounds = random.randint(0, self.width)

	def update(self, enemy_presence, ball_presence, ball_fired):
		#Creature makes a decision on what to do next

		#3 Inputs + 1 bias
		inputs = np.array([enemy_presence, ball_presence, ball_fired, 1])

		#Hidden Layer 1. 5 nodes
		l1 = sigmoid(np.dot(inputs, self.syn0))
		#Add bias
		l1 = np.append(l1, 1)

		#Hidden Layer 2. 5 nodes
		l2 = sigmoid(np.dot(l1, self.syn1))
		#Add bias
		l2 = np.append(l2, 1)

		#Output Layer. 5 outputs
		output = softmax(np.dot(l2, self.syn2))
		choice = np.random.choice(len(output), 1, p=output)[0]
		#choice = np.argmax(output)

		return choice

	def hit_target(self):
		self.fitness += 5

	def get_hit(self):
		if self.is_alive:
			self.health -=1
			self.fitness -= 1
			#print(self.health)

			if self.health <= 0:
				self.is_alive = False

	def shoot(self):
		self.bullet = Bullet(self.x, self.y, self.rotation)

if __name__ == '__main__':
	test = Creature()
	test.update(0,0,0)