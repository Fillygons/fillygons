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
min_angle = 60;

// Length on each end of an edge ehere no teeht are placed. This value works for angles as low as τ / 6.
corner_clearance = sqrt(3) * thickness / 2;

// Overhang of the ball dedents relative to the teeth surface.
dedent_sphere_offset = 0.5;

// Diameter of the ball dedent spheres.
dedent_sphere_dimeter = thickness;

// Diameter of the holes which accept the ball dedent spheres.
dedent_hole_diameter = 2.0;

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
	
	module trace(intersect = false) {
		module tail(i) {
			if (intersect) {
				intersection() {
					children();
					
					more(i) {
						tail(i + 1) {
							children();
						}
					}
				}
			} else {
				children();
				
				more(i) {
					tail(i + 1) {
						children();
					}
				}
			}
		}
		
		tail(0) {
			union() {
				children();
			}
		}
	}
	
	// The infintely extruded region of the polygon with an optional offset.
	module polygon(offset = 0) {
		trace(true) {
			sector_3d(ymin = offset);
		}
	}
	
	// The cylinders which form part of the teeth.
	module teeth_cylinders() {
		trace() {
			rotate([0, 90, 0]) {
				cylinder(h = side_length, r = thickness / 2);
			}
		}
	}
	
	// The whole part without any teeth or the hole cut out.
	module full_part() {
		intersection() {
			polygon();
			sector_3d(zmin = -thickness / 2, zmax = thickness / 2);
		}
		
		teeth_cylinders();
	}
	
	used_lenght = side_length - 2 * corner_clearance;
	tooth_width = used_lenght / (num_teeth * 2);
	
	function pos(pos) = corner_clearance + pos * tooth_width;
	function dir(pos) = 1 - pos % 2 * 2;
	
	module dedent_balls() {
		module ball(pos) {
			// Offset of the sphere's center relative to the tooth surface it is placed on.
			ball_offset = dedent_sphere_dimeter / 2 - dedent_sphere_offset + gap / 2;
			
			translate([pos(pos) + ball_offset * dir(pos), 0, 0]) {
				intersection() {
					sphere(d = dedent_sphere_dimeter);
					
					scale([dir(pos), 1, 1]) {
						sector_3d(xmax = 0);
					}
				}
			}
		}
		
		trace() {
			ball(1);
			ball(4);
		}
	}
		
	module dedent_holes() {
		// Offset of the sphere's center relative to the tooth surface it is placed on.
		module hole(pos) {
			translate([pos(pos), 0, 0]) {
				rotate([0, dir(pos) * 90, 0]) {
					translate([0, 0, gap / 2]) {
						cylinder(h = dedent_sphere_offset, d1 = dedent_hole_diameter, d2 = dedent_hole_diameter - 2 * dedent_sphere_offset);
					}
				}
			}
		}
		
		trace() {
			hole(2);
			hole(5);
		}
	}
	
	module clearance() {
		// The part to cut away inside the corner clearance so that two parts can join and rotate..
		module clearance_sections() {
			teeth_start = corner_clearance + gap / 2;
			
			sector_3d(ymax = gap / 2, xmin = 0, xmax = teeth_start);
			sector_3d(ymax = gap / 2, xmin = side_length - teeth_start, xmax = side_length);
		}
		
		trace() {
			clearance_sections();
			
			// To allow rotating two joined parts.
			rotate([90 - min_angle / 2, 0, 0]) {
				clearance_sections();
			}
		}
	}
	
	// The volume which is occupied by the teeth.
	// If invert is set to false, the region for the teeth and their dedent spheres is produced, if set to true, the region between the teeth and the dedent holes is produced.
	module teeth_gaps() {
		trace() {
			for (j = [0:num_teeth - 1]) {
				xmin = pos(2 * j + 1) - gap / 2;
				xmax = pos(2 * j + 2) + gap / 2;
				ymax = thickness / 2 + gap;
				
				sector_3d(xmin = xmin, xmax = xmax, ymax = ymax);
				
				// The part that needs to be removed to support acute angles.
				rotate([90 - min_angle, 0, 0]) {
					sector_3d(xmin = xmin, xmax = xmax, ymax = ymax);
				}
			}
		}
	}
	
	difference() {
		full_part();
		clearance();
		dedent_holes();
		teeth_gaps();
	}
	
	intersection() {
		full_part();
		dedent_balls();
	}
}

module regular_fillygon(num_sides) {
	fillygon([for (_ = [1:num_sides]) 180 - 360 / num_sides]);
}
