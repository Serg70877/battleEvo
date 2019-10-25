from pygame.math import Vector2
from helpers import constrainAngle
from creature import Creature

def moveStraight(creature, creature_speed):

	#Move forward or backwards
	movement = Vector2(0, creature_speed).rotate(creature.rotation)
	creature.y -= movement[1]
	creature.x += movement[0]

def advanceAntiClockwise(creature, creature_speed, rotation_speed):
					
	'''Using pygame Vector2 to calculate increase in X and Y.
	   In future should convert entire movement system to Vectors.'''
	creature.rotation = constrainAngle(creature.rotation, rotation_speed)

	movement = Vector2(0, creature_speed).rotate(creature.rotation)
	creature.y -= movement[1]
	creature.x += movement[0]
	if creature.rotation < 0 or creature.rotation > 360:
		print('AAC')
	creature.moving = True
	#print(f'Angle: {creature.rotation}')
	#print(f'Moved forward by {movement}')

def advanceClockwise(creature, creature_speed, rotation_speed):

	creature.rotation = constrainAngle(creature.rotation, -rotation_speed)

	movement = Vector2(0, creature_speed).rotate(creature.rotation)
	creature.y -= movement[1]
	creature.x += movement[0]
	if creature.rotation < 0 or creature.rotation > 360:
		print('AC')
	creature.moving = True
	#print(f'Angle: {creature.rotation}')
	#print(f'Moved backwards by {movement}')

def rotateAntiClockwise(creature, rotation_speed):
	'''if 360 - creature.rotation >= self.rotation_speed:
		creature.rotation += self.rotation_speed
		if creature.rotation == 360:
			creature.rotation = 0
	else:
		creature.rotation = self.rotation_speed - (360 - creature.rotation)'''

	creature.rotation = constrainAngle(creature.rotation, rotation_speed)

	creature.moving = False

	#print(f'Rotated anti-clockwise from {initial_rotation} to {creature.rotation}')

def rotateClockwise(creature, rotation_speed):

	'''if creature.rotation >= self.rotation_speed:
		creature.rotation -= self.rotation_speed
	else:
		creature.rotation = 360 - (self.rotation_speed - creature.rotation)'''

	creature.rotation = constrainAngle(creature.rotation, -rotation_speed)

	creature.moving = False

	#print(f'Rotated clockwise from {initial_rotation} to {creature.rotation}')

def shoot(creature):

	if creature.can_shoot == True:
		creature.can_shoot = False
		creature.shoot()
		#print('Shoot')
		#print(creature.bullet.direction)
	
	creature.moving = False
#print('-----')

def wrap(creature, creature_radius):

	#Wrap around
	if creature.y < 0 + creature_radius:
		creature.y = creature.height - creature_radius
	elif creature.y > creature.height - creature_radius:
		creature.y = 0 + creature_radius
	if creature.x < 0 + creature_radius:
		creature.x = creature.width - creature_radius
	elif creature.x > creature.width - creature_radius:
		creature.x = 0 + creature_radius

def constrainBounds(creature, creature_radius, bounds, screen_width):

	#Bounds = 0, left half. Bounds = 1, right half. Bounds = None, entire window
	#Constrain creature within bounds
	creature.y = min(creature.y, creature.height - creature_radius)
	creature.y = max(0 + creature_radius, creature.y)

	if bounds == 0:
		creature.x = min(creature.x, screen_width/2 - creature_radius - 50)
		creature.x = max(0 + creature_radius, creature.x)

	elif bounds == 1:
		creature.x = min(creature.x, creature.width - creature_radius)
		creature.x = max(screen_width/2 + creature_radius + 50, creature.x)

	else:
		creature.x = min(creature.x, creature.width - creature_radius)
		creature.x = max(0 + creature_radius, creature.x)