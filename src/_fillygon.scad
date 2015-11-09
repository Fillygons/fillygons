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
min_angle = acos(1 / 3) * rad;

// Length on each end of an edge ehere no teeht are placed.
corner_clearance = sqrt(3) * thickness / 2;

// Gap between touching surfaces.
gap = 0.2;

$fn = 8;

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
	
	// The 2D shape of the ideal polygon, optionally offset.
	module polygon(offset = 0) {
		module tail(i) {
			intersection() {
				sector_2d(ymin = offset);
				
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
		extrude(-thickness / 2, thickness / 2) {
			polygon();
		}
		
		teeth_cylinders();
	}
	
	// The part up until the border where the teeth start.
	module inner_part() {
		extrude(-thickness / 2, thickness / 2) {
			difference() {
				polygon(thickness / 2);
				polygon(loop_width);
			}
		}
	}
	
	// The volume which is occupied by the teeth.
	module teeth_region() {
		used_lenght = side_length - 2 * corner_clearance;
		tooth_width = used_lenght / num_teeth;
		
		module tail(i) {
			for (j = [0:num_teeth - 1]) {
				xmin = corner_clearance + j * tooth_width;
				
				sector_3d(xmin = xmin, xmax = xmin + tooth_width / 2, ymax = thickness / 2);
			}
			
			more(i) {
				tail(i + 1);
			}
		}
		
		tail(0);
	}
	
	intersection() {
		full_part();
		teeth_region();
	}
	
	inner_part();
}

module regular_fillygon(num_sides) {
	fillygon([for (_ = [1:num_sides]) 180 - 360 / num_sides]);
}
