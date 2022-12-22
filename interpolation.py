from shapely import geometry, ops

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
