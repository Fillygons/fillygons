include <_util.scad>

// Thickness of the pieces.
thickness = 4;

// Width of the rim along the edges of the piece connecting the teeth.
loop_width = 2 * thickness;

// Length of a pieces sides, measured along the ideal polygon's edges.
side_length = 40;

// Number of teeth along each side.
num_teeth = 3;

// Minimum dihedral alnge between this face and any other face.
min_angle = 40;

// Length on each end of an edge ehere no teeht are placed..
corner_clearance = 8;

// Overhang of the ball dedents relative to the teeth surface.
dedent_sphere_offset = 0.5;

// Diameter of the ball dedent spheres.
dedent_sphere_dimeter = thickness;

dedent_piece_width = 1.4;

dedent_piece_gap = 1;

// Diameter of the holes which accept the ball dedent spheres.
dedent_hole_diameter = 2.0;

// Gap between touching surfaces.
gap = 0.4;

$fn = 32;

module fillygon(angles) {
	module trace(intersect = false) {
		module more(i) {
			if (i < len(angles)) {
				translate([side_length, 0, 0]) {
					rotate(180 - angles[i]) {
						tail(i + 1) {
							children();
						}
					}
				}
			}
		}
		
		module tail(i) {
			if (intersect) {
				intersection() {
					union() {
						children();
					}
					
					more(i) {
						children();
					}
				}
			} else {
				children();
				
				more(i) {
					children();
				}
			}
		}
		
		tail(0) {
			children();
		}
	}
	
	used_lenght = side_length - 2 * corner_clearance;
	tooth_width = used_lenght / (num_teeth * 2);
	
	w = (side_length / 2 - corner_clearance - dedent_piece_width * 2 - dedent_piece_gap - gap) / 2;
	
	positions = [
		corner_clearance,
		corner_clearance + w,
		side_length / 2 - w,
		side_length / 2,
		side_length / 2 + w,
		side_length - corner_clearance - w,
		side_length - corner_clearance];
	
	function dir(pos) = 1 - pos % 2 * 2;
	function pos(pos) = positions[pos] + dir(pos) * gap / 2;
	
	// The infintely extruded region of the polygon with an optional offset.
	module edge(offset = 0) {
		sector_3d(ymin = offset);
	}
	
	// The cylinder which form part of the teeth.
	module teeth_cylinder() {
		rotate([0, 90, 0]) {
			extrude() {
				circle(d = thickness);
			}
		}
	}
	
	// The part to cut away inside the corner clearance so that two parts can join and rotate.
	module clearance_chamfer() {
		teeth_chamfer();
	}
	
	module clearance_region() {
		sector_3d(xmin = 0, xmax = pos(0));
		sector_3d(xmin = pos(num_teeth * 2), xmax = side_length);
	}
	
	module edge_region() {
		sector_3d(xmin = 0, xmax = side_length);
	}
	
	// The part that needs to be removed to support acute angles.
	module teeth_chamfer() {
		rotate([90 - min_angle, 0, 0]) {
			sector_3d(ymax = thickness / 2 + gap);
		}
		
		rotate([min_angle - 90, 0, 0]) {
			sector_3d(ymax = thickness / 2 + gap);
		}
	}
	
	// The volume of a dedent ball placed on a tooth at the specified position.
	module dedent_ball(pos) {
		// Offset of the sphere's center relative to the tooth surface it is placed on.
		ball_offset = dedent_sphere_dimeter / 2 - dedent_sphere_offset;
		
		translate([pos(pos), 0, 0]) {
			scale([dir(pos), 1, 1]) {
				intersection() {
					translate([ball_offset, 0, 0]) {
						sphere(d = dedent_sphere_dimeter);
					}
					
					// The ball needs to extend slightly past the origin because otherwise the final shape will have infinitely thin gaps.
					sector_3d(xmax = 0.1);
				}
			}
		}
	}
	
	module dedent_ball_cutting(pos) {
		translate([pos(pos), 0, 0]) {
			scale([dir(pos), 1, 1]) {
				sector_3d(xmin = dedent_piece_width, xmax = dedent_piece_width + dedent_piece_gap);
			}
		}
	}
	
	// The volume to remove from the teeth to create the hole for a ball dedent on a tooth at the specified position.
	module dedent_hole(pos) {
		translate([pos(pos), 0, 0]) {
			rotate([0, dir(pos) * 90, 0]) {
				cylinder(h = dedent_sphere_offset, d1 = dedent_hole_diameter, d2 = dedent_hole_diameter - 2 * dedent_sphere_offset);
			}
		}
	}
	
	// The volume which is occupied by the teeth. This includes the dedents and extends to infinity.
	module teeth_region() {
		balls = [4, 5];
		
		difference() {
			for (j = [0:num_teeth - 1]) {
				sector_3d(xmin = pos(2 * j), xmax = pos(2 * j + 1));
			}
			
			for (i = balls) {
				dedent_ball_cutting(i);
				dedent_hole(2 * num_teeth - i);
			}
		}
		
		for (i = balls) {
			dedent_ball(i);
		}
	}

	intersection() {
		difference() {
			union() {
				difference() {
					sector_3d(zmin = -thickness / 2, zmax = thickness / 2);
					trace() teeth_chamfer();
				}
				
				difference() {
					sector_3d(zmin = -thickness / 2, zmax = thickness / 2);
					trace() teeth_chamfer();
				}
				
				difference() {
					intersection() {
						sector_3d(zmin = -thickness / 2, zmax = thickness / 2);
						trace() intersection() {
							clearance_region();
							teeth_chamfer();
						}
							
					}
					
					trace() clearance_chamfer();
				}
				
				trace() intersection() {
					union() {
						teeth_cylinder();
						intersection() {
							sector_3d(zmin = -thickness / 2, zmax = thickness / 2);
							teeth_chamfer();
							edge();
						}
					}
					
					teeth_region();
				}
			}
			
			trace() intersection() {
				difference() {
					teeth_chamfer();
					teeth_region();
					clearance_region();
				}
				
				edge_region();
			}
			
			trace(true) edge(loop_width);
		}
		
		cube(1000, center = true);
	}
}

module regular_fillygon(num_sides) {
	fillygon([for (_ = [1:num_sides]) 180 - 360 / num_sides]);
}
