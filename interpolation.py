import math
from shapely import geometry, ops
from shapely.geometry import Point, Polygon, LineString, GeometryCollection
import numpy as np

def get_evenly_spaced_coordinates(line_string, segment_count = None, segment_length = None):
	print(line_string.length)
	print(len(line_string.coords))

	if segment_count == None:
		if segment_length == None:
			raise Exception("one of segmentCount and segmentLengh parameters needs to be specified")
		segment_count = line_string.length/segment_length

	return [line_string.interpolate(line_string.length*i/segment_count) for i in range(0, segment_count + 1)]

def three_point_cos(c1, c2, c3):
	a = np.array(c1)
	b = np.array(c2)
	c = np.array(c3)
	ba = a - b
	bc = c - b

	cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
	return np.degrees(np.arccos(cosine_angle))

def get_filtered_angles(coordinates, angle_threshold):
	def angle(c, i):
		return three_point_cos(c[i-1], c[i], c[i+1])

	angles = [(i, angle(coordinates, i), coordinates[i]) for i in range(1, len(coordinates)-1)]
	filtered_angles = filter(lambda t: t[1] < angle_threshold, angles)
	return filtered_angles

def get_coordinates_based_on_angles(line_string, threshold, angle_threshold):
	coordinates = list(line_string.coords)
	filtered_angles = get_filtered_angles(coordinates, angle_threshold)

	points = [Point(c) for i, a, c in filtered_angles]
	#print(points)
	points = [Point(coordinates[0])] + points + [Point(coordinates[-1])]

	return points

def noralize_angle_degrees(angle):
	return ((angle + 179) % 360 + 360) % 360 - 179


def get_projected_coordinates(coordinatesList, line):
	line_string = line

	def project_point(p):
		distance = line_string.project(p)
		return line_string.interpolate(distance)

	return list(map(project_point, coordinatesList))

def generate_line(lines, distance, evenSpread):
	print("line distance", distance)
	return LineString([line.interpolate(distance, normalized = evenSpread) for line in lines])

def enhance_coordinates_distribution(side_to_be_enchanced, second_side, enhanced_line_string, secon_line_string, distance_tharhold):
	#print(len(side_to_be_enchanced))

	enhanced_points = []
	second_points = []

	distances1 = [enhanced_line_string.project(point) for point in side_to_be_enchanced]
	distances2 = [secon_line_string.project(point) for point in second_side]

	# order is reversed - start inserting from the end to not disturb indices of not yet inserted points
	filtered_distance_list = [i-1 for i, v in enumerate(distances1) if abs(v - distances1[i-1]) > distance_tharhold][1:][::-1]
	print("points indices preceding too long gaps", filtered_distance_list)

	for v in filtered_distance_list:
		distance1 = distances1[v]
		distance2 = distances1[v+1]
		newPoint = enhanced_line_string.interpolate((distance1+distance2)/2)
		side_to_be_enchanced.insert(v+1, newPoint)
		enhanced_points.insert(v+1, newPoint)

		distance3 = distances2[v]
		distance4 = distances2[v+1]
		newPoint2 = secon_line_string.interpolate((distance3+distance4)/2)
		second_side.insert(v+1, newPoint2)
		second_points.insert(v+1, newPoint2)

	print(len(side_to_be_enchanced))
	return enhanced_points, second_points

def enhance_coordinates_distribution_based_on_angle(side_to_be_enchanced, second_side, enhanced_line_string, secon_line_string, distance_tharhold, angle_threshold):
	coordinates = list(enhanced_line_string.coords)
	filtered_angles = get_filtered_angles(coordinates, angle_threshold)
	
	distances = [enhanced_line_string.project(point) for point in side_to_be_enchanced]
	input_pairs = zip(distances, side_to_be_enchanced, second_side)
	input_list = list(input_pairs)
	#print(input_list)

	generated_points = [Point(a[2]) for a in filtered_angles]
	generated_distances = [enhanced_line_string.project(p) for p in generated_points]
	generated_second_points = [secon_line_string.interpolate(secon_line_string.project(p)) for p in generated_points]
	generated_pairs = zip(generated_distances, generated_points, generated_second_points)
	generated_list = list(generated_pairs)
	#print(generated_list)

	merged = input_list + generated_list
	
	merged.sort(key = lambda x: x[0])

	side_to_be_enchanced = [e for d, e, s in merged]
	second_side = [s for d, e, s in merged]
	return side_to_be_enchanced, second_side

def enhance_coordinates_distribution_all_the_way(side_to_be_enchanced, second_side, enhanced_line_string, secon_line_string, distance_tharhold):
	enhanced_points_accumulator = []
	second_points_accumulator = []

	enhanced, second = enhance_coordinates_distribution(side_to_be_enchanced, second_side, enhanced_line_string, secon_line_string, distance_tharhold)
	enhanced_points_accumulator += enhanced
	second_points_accumulator += second

	while len(enhanced) > 0:
		enhanced, second = enhance_coordinates_distribution(side_to_be_enchanced, second_side, enhanced_line_string, secon_line_string, distance_tharhold)
		enhanced_points_accumulator += enhanced
		second_points_accumulator += second

	return enhanced_points_accumulator, second_points_accumulator

def point_from_a_to_b_at_distance(a, b, distance):
	dx = b.x - a.x
	dy = b.y - a.y
	distance_factor = distance/math.sqrt(dx**2 + dy**2)

	return Point(a.x + dx*distance_factor, a.y + dy*distance_factor)
