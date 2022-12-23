from http.client import PROCESSING
import shapely
from shapely.geometry import Point, Polygon, LineString, GeometryCollection
from shapely import affinity
import geopandas as gpd
import matplotlib.pyplot as plt
import moviepy.editor as mp
import numpy as np
import os
from interpolation import * #get_evenly_spaced_coordinates
import util
import imageio
import os
from tkinter import *
import tk
import tkinter 
from tkinter import messagebox


top = tkinter.Tk()
top.title("Arc GEN")
label_list = [
     ["Arc generator",            0]
    ,["Line width",               0.35]
    ,["Layer height",             0.4]
    ,["Arc extrusion multiplier", 1.05]
    ,["Feedrate",                 2]
    ,["BrimWidth",                5]
    ,["Overhang Height",          20]
    ,["Filament DIA",             1.75]
    ,["Base Height",              0.5]
    ,["Max circle radius",        10]
    ,["Min circle radius",        2]
    ,["Points per circle",        40]
    ,["Radius of random polygon", 10]
    ,["Polygon irregularity",     0.5]
    ,["Polygon spikiness",        0.3]
    ,["Polygon num vertices",     15]
    ,["X Axis position",          100]
    ,["Y Axis position",          50]]
L = []
for i, label in enumerate(label_list):
    L.append("nothing")
    L[i] = Label(top, text=label_list[i][0],).grid(row=i,column=0)


E = []
for i in range(len(label_list)-1):
    E.append("nothing")
    E[i] = Entry(top, bd =5)
    E[i].grid(row = i+1,column=1)
    E[i].insert(i, str(label_list[i+1][1]))

def proces():
    global LINE_WIDTH
    i = 0
    LINE_WIDTH=float(Entry.get(E[i]))
    i += 1
    global LAYER_HEIGHT
    LAYER_HEIGHT = float(Entry.get(E[i]))
    i += 1
    global ARC_E_MULTIPLIER
    ARC_E_MULTIPLIER = float(Entry.get(E[i]))
    i += 1
    global FEEDRATE
    FEEDRATE = float(Entry.get(E[i]))
    i += 1
    global BRIM_WIDTH
    BRIM_WIDTH = float(Entry.get(E[i]))
    i += 1
    global OVERHANG_HEIGHT
    OVERHANG_HEIGHT = float(Entry.get(E[i]))
    i += 1
    global FILAMENT_DIAMETER
    FILAMENT_DIAMETER = float(Entry.get(E[i]))
    i += 1
    global BASE_HEIGHT
    BASE_HEIGHT = float(Entry.get(E[i]))
    i += 1
    global R_MAX
    R_MAX = float(Entry.get(E[i]))
    i += 1
    global R_MIN
    R_MIN = float(Entry.get(E[i]))
    i += 1
    global N
    N = float(Entry.get(E[i]))
    i += 1
    global  avg_radius
    avg_radius = float(Entry.get(E[i]))
    i += 1
    global irregularity
    irregularity = float(Entry.get(E[i]))
    i += 1
    global spikiness
    spikiness = float(Entry.get(E[i]))
    i += 1
    global num_vertices
    num_vertices = float(Entry.get(E[i]))
    i += 1
    global x_axis
    x_axis = float(Entry.get(E[i]))
    i += 1
    global y_axis
    y_axis = float(Entry.get(E[i]))
    top.destroy()

B=Button(top, text ="Generate",command= proces).grid(row=19,column=1)
#top.mainloop()
proces()

# Hard-coded recursion information
THRESHOLD = R_MIN  #5 # How much of a 'buffer' the arcs leave around the base polygon. Don't set it negative or bad things happen.
MIN_ARCS = np.floor(R_MIN/LINE_WIDTH)
OUTPUT_FILE_NAME = "output/output.gcode"

# Create a figure that we can plot stuff onto
fig, ax = plt.subplots(1, 2)
ax[0].set_aspect('equal')
ax[1].set_aspect('equal')
ax[0].title.set_text('Gcode Preview')
ax[1].title.set_text('Rainbow Visualization')

# Create a list of image names
image_name_list = []

# Delete all previous images
current_directory = "./"
files_in_directory = os.listdir(current_directory)
for item in files_in_directory:
    if item.endswith(".png"):
        os.remove(os.path.join(current_directory, item))

# Create a new gcode file
os.makedirs(os.path.dirname(OUTPUT_FILE_NAME), exist_ok=True)
with open(OUTPUT_FILE_NAME, 'w') as gcode_file:
    gcode_file.write(""";gcode for ArcOverhang. Created by Steven McCulloch\n""")

# Add start gcode
with open('input/start.gcode','r') as start_gcode, open(OUTPUT_FILE_NAME,'a') as gcode_file:
    for line in start_gcode:
        gcode_file.write(line)

# Create base polygon. The base polygon is the shape that will be filled by arcs
#base_poly = util.create_rect(150, 20, 20, 20, True)
base_poly = util.create_rect(150, 20, 20, 30, True)

# Make the base polygon a randomly generated shape
#base_poly = Polygon(util.generate_polygon(center=(x_axis, y_axis), avg_radius=avg_radius, irregularity=irregularity, spikiness=spikiness, num_vertices=num_vertices,))

base_poly = Polygon([(105.65561662438037, 36.68752056996291), (108.77720450830691, 41.74945197365837), (105.17360504052347, 47.09145282687201), (110.91842393825652, 47.13518103973508), (111.41386054680402, 50.33605461197101), (107.04510551892349, 54.47702932950298), (108.416931200917, 62.79195975377525), (100.20919201800629, 59.804595628659015), (95.87491051840271, 57.819578790826824), (91.85621006974287, 57.919926017940796), (90.99658176429888, 51.71709533723465), (91.14418335612086, 46.12348195605352), (91.7392323668236, 41.5426483038725), (94.2444771612594, 35.61503290564059), (102.1338271220903, 38.18127709742047), (105.65561662438037, 36.68752056996291)])
#base_poly = Polygon([(95.03307591266207, 61.44242332237353), (93.2611944512131, 54.03978522828941), (84.18173584271653, 50.71604934203349), (87.85468744487517, 42.61007177424688), (90.4103518773317, 40.55211002769791), (95.13321538102718, 42.227355495114075), (96.83477977873106, 38.14555774373097), (99.65886967537523, 38.98265402628894), (103.4901975249252, 40.25797485017517), (109.69626582291217, 42.55380147688191), (103.84477881018918, 48.603689008861444), (104.97768296404406, 50.63600468887961), (107.4394892600432, 56.047883366279436), (104.4248669124622, 58.060614733550565), (98.96258436494416, 57.162750031589866), (95.03307591266207, 61.44242332237353)])

# Find starting edge (in this implementation, it just finds the largest edge to start from.
# TODO Allow multiple starting points
# TODO Come up with some way to determine starting edges based on geometry of previous layer
 
p1, p2 = util.longest_edge(base_poly)
starting_line = LineString([p1, p2])

# Copy the base polygon, but exclude the starting (longest) line, turning it from a closed Polygon to an open LineString
boundary_line = LineString(util.get_boundary_line(base_poly, p1))

# Create the first arc
starting_point, r_start, r_farthest = util.get_farthest_point(starting_line, boundary_line, base_poly)
starting_circle_norot = util.create_circle(starting_point.x, starting_point.y, r_start, N)
starting_line_angle = np.arctan2((p2.y-p1.y),(p2.x-p1.x))
starting_circle = affinity.rotate(starting_circle_norot, starting_line_angle, origin = 'centroid', use_radians=True)
starting_arc = starting_circle.intersection(base_poly)

# plot base poly
base_poly_geoseries = gpd.GeoSeries(base_poly)
base_poly_geoseries.plot(ax=ax[0], color='white', edgecolor='black', linewidth=1)
base_poly_geoseries.plot(ax=ax[1], color='white', edgecolor='black', linewidth=1)

# plot starting line
starting_line_geoseries = gpd.GeoSeries(starting_line)
starting_line_geoseries.plot(ax=ax[0], color='red', linewidth=2)

# Generate 3d printed starting tower
curr_z = LAYER_HEIGHT  # Height of first layer
with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
    gcode_file.write(f"G0 X{'{0:.3f}'.format(starting_point.x)} Y{'{0:.3f}'.format(starting_point.y)} F500\n")
    gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")
    gcode_file.write(";Generating first layer\n")
    gcode_file.write("G1 E3.8\n")  # Unretract
    
# Fill in circles from outside to inside
while curr_z < BASE_HEIGHT:
    starting_tower_r = r_start + BRIM_WIDTH  
    while starting_tower_r > LINE_WIDTH*2:
        first_layer_circle = util.create_circle(starting_point.x, starting_point.y, starting_tower_r, N)
        util.write_gcode(OUTPUT_FILE_NAME, first_layer_circle, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, 2, FEEDRATE*5, close_loop=True)
        starting_tower_r -= LINE_WIDTH*2
    
    curr_z += LAYER_HEIGHT
    with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
        gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")

with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
    gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")
    gcode_file.write(";Generating tower\n")
    gcode_file.write("M106 S255 ;Turn on fan to max power\n") 
    
while curr_z < OVERHANG_HEIGHT:
    util.write_gcode(OUTPUT_FILE_NAME, starting_line.buffer(LINE_WIDTH), LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, 2, FEEDRATE*5, close_loop=True)
    with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
        gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")
    curr_z += LAYER_HEIGHT

curr_z -= LAYER_HEIGHT*2

with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
        gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z)} F500\n")

# Create multiple layers
r = LINE_WIDTH
small_arc_radius = 0.5 # Arcs smaller than this get reduced speed and/or flow settings.
curr_arc = starting_arc

# Overlap arc with the starting line
starting_point = util.move_toward_point(starting_point, affinity.rotate(p1, 90, LineString([p1, p2]).centroid), LINE_WIDTH*0.5) 

# Create arcs until we reach the edge of the polygon
while r < r_start-THRESHOLD:

    # Create a circle based on point location, radius, n
    next_circle = Polygon(util.create_circle(starting_point.x, starting_point.y, r, N))
    next_circle = affinity.rotate(next_circle, starting_line_angle, origin = 'centroid', use_radians=True)

    # Plot arc
    next_arc = util.create_arc(next_circle, base_poly, ax, depth=0)
    if not next_arc:
        r += LINE_WIDTH
        continue
    curr_arc = Polygon(next_arc)

    #Slow down and reduce flow for all small arcs
    if r < small_arc_radius:
        speed_modifier = 0.25
        e_modifier = 0.25
    else: 
        speed_modifier = 1
        e_modifier = 1

    # Write gcode to file
    util.write_gcode(OUTPUT_FILE_NAME, next_arc, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, ARC_E_MULTIPLIER*e_modifier, FEEDRATE*speed_modifier, close_loop=False)
    
    r += LINE_WIDTH
    
    # Create image
    #file_name = util.image_number(image_name_list)   
    #plt.savefig(file_name, dpi=200)
    #image_name_list.append(file_name + ".png")

remaining_empty_space = base_poly.difference(curr_arc)
next_point, longest_distance, _ = util.get_farthest_point(curr_arc, boundary_line, base_poly)

# If there's room for an arc to be built on top of the current arc, then do it!
while longest_distance > THRESHOLD + MIN_ARCS*LINE_WIDTH: 
    next_arc, remaining_empty_space, image_name_list = util.arc_overhang(curr_arc, boundary_line, starting_line_angle, N, 
                                                                        remaining_empty_space, next_circle, 
                                                                        THRESHOLD, ax, fig, 1, image_name_list, 
                                                                        R_MAX, MIN_ARCS, LINE_WIDTH, OUTPUT_FILE_NAME,
                                                                        LAYER_HEIGHT, FILAMENT_DIAMETER, ARC_E_MULTIPLIER,
                                                                        FEEDRATE)
    next_point, longest_distance, _ = util.get_farthest_point(curr_arc, boundary_line, remaining_empty_space)

# interpolation
shape_target = boundary_line.simplify(0)
if shape_target.geom_type == 'MultiLineString':
    shape_target = ops.linemerge(shape_target)
#shape_completed = remaining_empty_space.exterior.difference(boundary_line).difference(starting_line)
shape_completed = remaining_empty_space.exterior.difference(boundary_line)
if shape_completed.geom_type == 'MultiLineString':
    shape_completed = ops.linemerge(shape_completed)

analizis_geoseries = gpd.GeoSeries(shape_target)
analizis_geoseries.plot(ax=ax[0], color='magenta', linewidth=4)

printed_geoseries = gpd.GeoSeries(shape_completed) # already printed part
printed_geoseries.plot(ax=ax[0], color='lime', linewidth=4)

interpolation_pointsd_distance = 1
divisions = int(shape_completed.length/interpolation_pointsd_distance)
points_target = get_coordinates_based_on_angles(shape_target, interpolation_pointsd_distance, 175)
#points_target = get_evenly_spaced_coordinates(shape_target, divisions)
points_completed = get_projected_coordinates(points_target, shape_completed)
#points2 = get_evenly_spaced_coordinates(shape_completed, divisions)
#points2 = get_evenly_spaced_coordinates(shape_completed, divisions)[::-1]

print("angle enhanced", len(points_completed))
points_completed, points_target = enhance_coordinates_distribution_based_on_angle(points_completed, points_target, shape_completed, shape_target, interpolation_pointsd_distance, 130)
print("angle enhanced", len(points_completed))

newPoints2, newPoints1 = enhance_coordinates_distribution_all_the_way(points_completed, points_target, shape_completed, shape_target, interpolation_pointsd_distance)
#newPoints4, newPoints3 = enhance_coordinates_distribution(points_completed, points_target, shape_completed, shape_target, interpolation_pointsd_distance)
print(len(points_completed))

# draw points
if False:
    for point in points_target:
        gpd.GeoSeries(point).plot(ax=ax[0], color='red', linewidth=4)
    for point in points_completed:
        gpd.GeoSeries(point).plot(ax=ax[0], color='blue', linewidth=4)

point_pairs = zip(points_target, points_completed)
interpolation_lines = [LineString(list(pair)) for pair in point_pairs]

# draw interpolation lines
if False:
    for line in interpolation_lines:
        gpd.GeoSeries(line).plot(ax=ax[0], color='darkgray', linewidth=1)

max_length = max([line.length for line in interpolation_lines])
contorus_count = int(max_length/LINE_WIDTH)
print(max_length, LINE_WIDTH, contorus_count)

contours = [generate_line(interpolation_lines, (i+1)/contorus_count) for i in range(contorus_count)]

# draw contours
if True:
    for line in contours:
        gpd.GeoSeries(line).plot(ax=ax[0], color='blue', linewidth=1)


# Add concentric rings around the outside of the perimeter
# TODO don't use a for loop.....
# TODO write interpolation here
"""
for i in range(100):
    first_ring = LineString(Polygon(boundary_line).buffer(-99*LINE_WIDTH + LINE_WIDTH*i).exterior.coords)
    first_ring = first_ring.intersection(remaining_empty_space)
    if first_ring.length <1e-9:
        continue

    if first_ring.geom_type == 'LineString':
        line = first_ring
        # plot starting line
        first_ring_geoseries = gpd.GeoSeries(line)
        first_ring_geoseries.plot(ax=ax[0], color='blue', edgecolor = 'blue', linewidth=1)
        util.write_gcode(OUTPUT_FILE_NAME, line, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, ARC_E_MULTIPLIER, FEEDRATE, False)
    else:
        for line in first_ring.geoms:
            # plot starting line
            first_ring_geoseries = gpd.GeoSeries(line)
            first_ring_geoseries.plot(ax=ax[0], color='blue', edgecolor = 'blue', linewidth=1)
            util.write_gcode(OUTPUT_FILE_NAME, line, LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, ARC_E_MULTIPLIER, FEEDRATE, False)

            #Make image
            #file_name = util.image_number(image_name_list)   
            #plt.savefig(file_name, dpi=200)
            #image_name_list.append(file_name + ".png")
"""

"""
# Turn images into gif + MP4
print("Making gif")
with imageio.get_writer('output/output_gif.gif', mode='I', fps=20) as writer:
    for file_name in image_name_list:
        image = imageio.imread(file_name)
        writer.append_data(image)

print("Making movie")
clip = mp.VideoFileClip("output/output_gif.gif")
clip.write_videofile("output/output_video.mp4")
"""
# Build a few layers on top of the overhanging area
for i in range(10):
    util.write_gcode(OUTPUT_FILE_NAME, Polygon(boundary_line).buffer(-LINE_WIDTH/2), LINE_WIDTH, LAYER_HEIGHT, FILAMENT_DIAMETER, ARC_E_MULTIPLIER, FEEDRATE*3, close_loop=True)
    with open(OUTPUT_FILE_NAME, 'a') as gcode_file:
        gcode_file.write(f"G1 Z{'{0:.3f}'.format(curr_z+LAYER_HEIGHT*i)} F500\n")
        
# Write end gcode
with open('input/end.gcode','r') as end_gcode, open(OUTPUT_FILE_NAME,'a') as gcode_file:
    for line in end_gcode:
        gcode_file.write(line)

print("base_poly coordinates to copy: ", list(base_poly.exterior.coords))

# Create image
plt.savefig("output/output", dpi=600)
plt.show()
