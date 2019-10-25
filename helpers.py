import math
import pygame

def gameIterator(competitors):

	for competitor1 in competitors:
		for competitor2 in competitors:
			#Ensure that creatures cannot be matched against themselves
			if competitor1 != competitor2:
				yield [competitor1, competitor2]

def check_collision(object1, radius1, object2, radius2):
	#Returns true if there is a collision
	return (object1.x - radius1 < object2.x + radius2 and 
	            object1.x + radius1 > object2.x - radius2 and
	            object1.y + radius1 > object2.y - radius2 and
	            object1.y - radius1 < object2.y + radius2)


def constrainAngle(angle, change):

	if angle + change > 360:
		angle = (angle + change) - 360
	elif angle + change < 0:
		angle = 360 - abs(angle + change)
	elif angle + change == 360:
		return 0
	else:
		return angle + change
	if angle == 360:
		angle = 0
	return angle

def hypotenuse(x, y):
	return math.hypot(x, y)

def calculateLOS(target_creature, delta_x, delta_y, vision_range, quadrant):
	#Calculates if object is in target's LOS
	if quadrant == 1:
		#0 degree line is straight up
		theta = 90 - math.degrees(math.atan(delta_y/delta_x)) #Theta is the angle of creature from the 0 degree line

		if theta - vision_range < 0:
			min_theta = 360 - abs(theta - vision_range)

			if target_creature.rotation >= min_theta or target_creature.rotation <= theta + vision_range:
					return hypotenuse(delta_x, delta_y)
			else:
					return 0
		else:
			if target_creature.rotation >= theta - vision_range and target_creature.rotation <= theta + vision_range:
				return hypotenuse(delta_x, delta_y)
			else:
				return 0

	elif quadrant == 2:
		theta = 90 + math.degrees(math.atan(delta_y/delta_x))

		if target_creature.rotation >= theta - vision_range and target_creature.rotation <= theta + vision_range:
				return hypotenuse(delta_x, delta_y)
		else:
				return 0

	elif quadrant == 3:
		theta = 270 - math.degrees(math.atan(delta_y/delta_x))

		if target_creature.rotation >= theta - vision_range and target_creature.rotation <= theta + vision_range:
				return hypotenuse(delta_x, delta_y)
		else:
				return 0

	elif quadrant == 4:
		theta = 270 + math.degrees(math.atan(delta_y/delta_x))

		if theta + vision_range >= 360:
			max_theta = (theta + vision_range - 360)
			if target_creature.rotation <= max_theta or (target_creature.rotation <= 360 and target_creature.rotation >= theta - vision_range):
				return hypotenuse(delta_x, delta_y)
			else:
				return 0
		else:
			if target_creature.rotation >= theta - vision_range and target_creature.rotation <= theta + vision_range:
				return hypotenuse(delta_x, delta_y)
			else:
				return 0

	elif quadrant == 5:
		#Directly above
		theta = 0

		if target_creature.rotation >= 360 - vision_range or target_creature.rotation <= 0 + vision_range:
			return delta_y
		else:
			return 0

	elif quadrant == 6:
		#Directly below
		theta = 180
		if target_creature.rotation >= theta - vision_range and target_creature.rotation <= theta + vision_range:
			return delta_y
		else:
			return 0

	elif quadrant == 7:
		#Directly to the left
		theta = 90
		if target_creature.rotation >= theta - vision_range and target_creature.rotation <= theta + vision_range:
			return delta_y
		else:
			return 0

	else:
		#Directly to the right
		theta = 270
		if target_creature.rotation >= theta - vision_range and target_creature.rotation <= theta + vision_range:
			return delta_y
		else:
			return 0