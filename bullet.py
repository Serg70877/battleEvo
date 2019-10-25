import json
from pygame.math import Vector2

class Bullet():
	def __init__(self, x, y, direction):

		with open("config.json") as cfg:
			config = json.load(cfg)

		self.width = config['width']
		self.height = config['height']
		self.bullet_speed = config['bullet_speed']

		config = None

		self.x = x
		self.y = y
		self.direction = direction

	def update(self):
		#Returns True if out of bounds

		#Move bullet
		movement = Vector2(0, self.bullet_speed).rotate(self.direction)
		self.y -= movement[1]
		self.x += movement[0]

		if self.x < 0 or self.y < 0 or self.x > self.width or self.y > self.height:
			return True
		else:
			return False
