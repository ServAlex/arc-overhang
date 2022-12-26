;Start gcode
M117 starting
;M140 S60
;M104 S195 ;colder temps help the overhang cool down faster
;M190 S60
;M109 S195
;G28             
;#G1 X100 Y5 Z1.5 F9000 ; Prime line
M83 						;relative extrusion
;G1 X130 E30 F100 ; Draw prime line
;G1 E-4 F1500; Retract 4mm. Adjust this as needed
;M201 X2500 Y2500 Z500 E5000	; set max acceleration, not supported on klipper
;M203 X200 Y200 Z50 E100		; set max feed rate, not supported on klipper
;M205 X15 Y15 Z15 E15			; firmware dependent, min travel speed on marlin, not supported on klipper

M117 waiting for temp
M109 S190 						; set temperature and wait for it to be reached
M190 S60 						; set bed temperature and wait for it to be reached
M117 print_start
PRINT_START EXTRUDER=191 BED=61

M117 start completed
G90                            ; absolute positioning