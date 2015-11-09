include <_util.scad>

// Thickness of the pieces.
thickness = 4;

// Width of the rim along the edges of the piece connecting the teeth.
loop_width = 1.5 * thickness;

// Length of a pieces sides, measured along the ideal polygon's edges.
side_length = 30;

// Number of teeth along each side.
num_teeth = 3;

// Minimum dihedral alnge between this face and any other face.
min_angle = acos(1 / 3);

// Length on each end of an edge ehere no teeht are placed. This value works for angles as low as τ / 6.
corner_clearance = sqrt(3) * thickness / 2;

// Overhang of the ball dedents relative to the teeth surface.
dedent_sphere_offset = 0.6;

// Diameter of the ball dedent spheres.
dedent_sphere_dimeter = thickness;

// Diameter of the holes which accept the ball dedent spheres.
dedent_hole_diameter = 2.6;

// Gap between touching surfaces.
gap = 0.4;

$fn = 32;

module fillygon(angles) {
	module more(i) {
		if (i < len(angles)) {
			translate([side_length, 0, 0]) {
				rotate(180 - angles[i]) {
					children();
				}
			}
		}
	}
	
	// The infintely extruded region of the polygon with an optional offset.
	module polygon(offset = 0) {
		module tail(i) {
			intersection() {
				sector_3d(ymin = offset);
				
				more(i) {
					tail(i + 1);
				}
			}
		}
		
		tail(0);
	}
	
	// The cylinders which form part of the teeth.
	module teeth_cylinders() {
		module tail(i) {
			rotate([0, 90, 0]) {
				cylinder(h = side_length, r = thickness / 2);
			}
			
			more(i) {
				tail(i + 1);
			}
		}
		
		tail(0);
	}
	
	// The whole part without any teeth or the hole cut out.
	module full_part() {
		intersection() {
			polygon();
			sector_3d(zmin = -thickness / 2, zmax = thickness / 2);
		}
		
		teeth_cylinders();
	}
	
	// The volume which is occupied by the teeth.
	// If invert is set to false, the region for the teeth and their dedent spheres is produced, if set to true, the region between the teeth and the dedent holes is produced.
	module teeth_region(invert = false) {
		used_lenght = side_length - 2 * corner_clearance;
		tooth_width = used_lenght / (num_teeth * 2);
		
		function pos(pos) = corner_clearance + pos * tooth_width;
		
		// Offset added on both sides of the teeth.
		hgap = gap / 2 * (invert ? 1 : -1);
		
		module tail(i) {
			module teeth() {
				for (j = [0:num_teeth - 1]) {
					offset = invert ? 1 : 0;
					xmin = pos(2 * j + offset) - hgap;
					xmax = pos(2 * j + offset + 1) + hgap;
					ymax = thickness / 2 + gap;
					
					sector_3d(xmin = xmin, xmax = xmax, ymax = ymax);
					
					// The part that needs to be removed to support acute angles.
					if (invert) {
						rotate([90 - min_angle, 0, 0]) {
							sector_3d(xmin = xmin, xmax = xmax, ymax = ymax, zmax = 0);
						}
					}
				}
			}
			
			module dedent_balls() {
				// Offset of the sphere's center relative to the tooth surface it is placed on.
				ball_offset = dedent_sphere_dimeter / 2 - dedent_sphere_offset + hgap;
				
				translate([pos(2) + ball_offset, 0, 0]) {
					sphere(d = dedent_sphere_dimeter);
				}
				
				translate([pos(5) - ball_offset, 0, 0]) {
					sphere(d = dedent_sphere_dimeter);
				}
			}
			
			module dedent_holes() {
				// Offset of the sphere's center relative to the tooth surface it is placed on.
				module hole_shape() {
					translate([hgap, 0, 0]) {
						rotate([0, 90, 0]) {
							cylinder(h = dedent_sphere_offset, d1 = dedent_hole_diameter, d2 = dedent_hole_diameter - 2 * dedent_sphere_offset);
						}
					}
				}
				
				translate([pos(4), 0, 0]) {
					hole_shape();
				}
				
				translate([pos(1), 0, 0]) {
					scale([-1, 1, 1]) {
						hole_shape();
					}
				}
			}
			
			// The part to cut away inside the corner clearance so that two parts can join and rotate..
			module clearance() {
				teeth_start = corner_clearance + hgap;
				
				sector_3d(ymax = hgap, xmin = 0, xmax = teeth_start);
				sector_3d(ymax = hgap, xmin = side_length - teeth_start, xmax = side_length);
			}
			
			// Deciding which elements to add and subtract involves some magic. Here we decide which elements need to be part of the positive and negative regions which define the teeth.
			if (invert) {
				difference() {
					teeth();
					dedent_balls();
				}
				
				dedent_holes();
				clearance();
				
				// To allow rotating two joined parts.
				rotate([90 - min_angle / 2, 0, 0]) {
					clearance();
				}
			} else {
				teeth();
				dedent_balls();
			}
			
			more(i) {
				tail(i + 1);
			}
		}
		
		tail(0);
	}
	
	intersection() {
		full_part();
		
		// Add the teeht before removing the gaps between the teeth to prevent teeth from bleeding into the gaps on acute angles.
		difference() {
			union() {
				polygon();
				teeth_region();
			}
			
			teeth_region(true);
			polygon(loop_width);
		}
	}
}

module regular_fillygon(num_sides) {
	fillygon([for (_ = [1:num_sides]) 180 - 360 / num_sides]);
}
