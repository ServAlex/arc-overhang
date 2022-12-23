from shapely import geometry, ops
from shapely.geometry import Point, Polygon, LineString, GeometryCollection

def get_evenly_spaced_coordinates(line, segmentCount = None, segmentLength = None):
	print(line.length)
	print(line.geom_type)
	lineString = line
	if line.geom_type == 'MultiLineString':
		lineString = ops.linemerge(line)
	print(len(lineString.coords))

	if segmentCount == None:
		if segmentLength == None:
			raise Exception("one of segmentCount and segmentLengh parameters needs to be specified")
		segmentCount = lineString.length/segmentLength

	return [lineString.interpolate(lineString.length*i/segmentCount) for i in range(0, segmentCount + 1)]


def get_projected_coordinates(coordinatesList, line):
	lineString = line
	if line.geom_type == 'MultiLineString':
		lineString = ops.linemerge(line)

	def projectPoint(p):
		distance = lineString.project(p)
		return lineString.interpolate(distance)

	return list(map(projectPoint, coordinatesList))

def generate_line(lines, distance):
	print(distance)
	return LineString([line.interpolate(distance, normalized = True) for line in lines])

def enhance_coordinates_distribution(sideToBeEnchanced, secondSide, enhancedLineString, seconLineString, distanceTharhold):
	# project!
	print(len(sideToBeEnchanced))
	#print(secondSide)

	if enhancedLineString.geom_type == 'MultiLineString':
		enhancedLineString = ops.linemerge(enhancedLineString)
	if seconLineString.geom_type == 'MultiLineString':
		seconLineString = ops.linemerge(seconLineString)

	enhancedPoints = []
	secondPoints = []

	#print([tuple(point.coords) for point in sideToBeEnchanced])
	#print([tuple(point.coords) for point in secondSide])
	#filteredDistanceList = [(i-1, x.distance(sideToBeEnchanced[i - 1])) for i, x in enumerate(sideToBeEnchanced) if x.distance(sideToBeEnchanced[i - 1]) > distanceTharhold][1:]
	#filteredDistanceList = [i-1 for i, x in enumerate(sideToBeEnchanced) if x.distance(sideToBeEnchanced[i - 1]) > distanceTharhold][1:]
	distances1 = [enhancedLineString.project(point) for point in sideToBeEnchanced]
	distances2 = [seconLineString.project(point) for point in secondSide]
	filteredDistanceList = [i-1 for i, v in enumerate(distances1) if abs(v - distances1[i-1]) > distanceTharhold][1:][::-1]
	print(filteredDistanceList)

	# insert starting from the end!

	for v in filteredDistanceList:
		distance1 = distances1[v]
		distance2 = distances1[v+1]
		newPoint = enhancedLineString.interpolate((distance1+distance2)/2)
		sideToBeEnchanced.insert(v+1, newPoint)
		enhancedPoints.insert(v+1, newPoint)


		distance3 = distances2[v]
		distance4 = distances2[v+1]
		newPoint2 = seconLineString.interpolate((distance3+distance4)/2)
		secondSide.insert(v+1, newPoint2)
		secondPoints.insert(v+1, newPoint2)

	#print(sideToBeEnchanced)
	print(len(sideToBeEnchanced))
	return enhancedPoints, secondPoints



