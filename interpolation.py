from shapely import geometry, ops
from shapely.geometry import Point, Polygon, LineString, GeometryCollection

def get_evenly_spaced_coordinates(line, segment_count = None, segment_length = None):
	print(line.length)
	print(line.geom_type)
	line_string = line
	if line.geom_type == 'MultiLineString':
		line_string = ops.linemerge(line)
	print(len(line_string.coords))

	if segment_count == None:
		if segment_length == None:
			raise Exception("one of segmentCount and segmentLengh parameters needs to be specified")
		segment_count = line_string.length/segment_length

	return [line_string.interpolate(line_string.length*i/segment_count) for i in range(0, segment_count + 1)]


def get_projected_coordinates(coordinatesList, line):
	line_string = line
	if line.geom_type == 'MultiLineString':
		line_string = ops.linemerge(line)

	def project_point(p):
		distance = line_string.project(p)
		return line_string.interpolate(distance)

	return list(map(project_point, coordinatesList))

def generate_line(lines, distance):
	print(distance)
	return LineString([line.interpolate(distance, normalized = True) for line in lines])

def enhance_coordinates_distribution(side_to_be_enchanced, second_side, enhanced_line_string, secon_line_string, distance_tharhold):
	print(len(side_to_be_enchanced))

	if enhanced_line_string.geom_type == 'MultiLineString':
		enhanced_line_string = ops.linemerge(enhanced_line_string)
	if secon_line_string.geom_type == 'MultiLineString':
		secon_line_string = ops.linemerge(secon_line_string)

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



