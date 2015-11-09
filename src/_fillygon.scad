include <_util.scad>

// Thickness of the pieces.
thickness = 4;

// Width of the rim along the edges of the piece connecting the teeth.
border_width = 1.5 * thickness;

// Length of a pieces sides, measured along the ideal polygon's edges.
side_length = 30;

// Number of teeth along each side.
num_teeth = 3;

// Minimum dihedral alnge between this face and any other face.
min_angle = acos(1 / 3) * rad;

// Length on each end of an edge ehere no teeht are placed.
corner_clearance = 3;

// Gap between touching surfaces.
gap = 0.2;

$fn = 16;

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
	
	// The 2D shape of the ideal polygon.
	module ideal_polygon() {
		module tail(i) {
			intersection() {
				half_plane();
				
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
	
	// The whole part without the gaps between the teeth cut out.
	module border() {
		translate([0, 0, -thickness / 2]) {
			linear_extrude(thickness) {
				difference() {
					ideal_polygon();
					
					offset(-border_width) {
						ideal_polygon();
					}
				}
			}
		}
		
		teeth_cylinders();
	}
	
	// The volume which is cut out from the cylinders and the border to for the teeth.
	module teeth_gaps() {
		used_lenght = side_length - 2 * corner_clearance;
		tooth_width = used_lenght / num_teeth;
		
		module tail(i) {
			intersection() {
				intersection_for (j = [0:num_teeth - 1]) {
					translate([corner_clearance + j * tooth_width, 0, 0]) {
						union() {
							rotate([0, -90, 0]) {
								half_space();
							}
							
							translate([tooth_width / 2, 0, 0]) {
								rotate([0, 90, 0]) {
									half_space();
								}
							}
						}
					}
				}
				
				translate([0, thickness / 2]) {
					rotate([90, 0, 0]) {
						half_space();
					}
				}
			}
			
			more(i) {
				tail(i + 1);
			}
		}
		
		tail(0);
	}
	
	difference() {
		border();
		teeth_gaps();
	}
}

module regular_fillygon(num_sides) {
	fillygon([for (_ = [1:num_sides]) 180 - 360 / num_sides]);
}
