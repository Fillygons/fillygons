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
min_angle = 55;

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
	
	function dir(pos) = 1 - pos % 2 * 2;
	function pos(pos) = corner_clearance + pos * tooth_width + dir(pos) * gap / 2;
	
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
	
	module dedent_ball(pos) {
		// Offset of the sphere's center relative to the tooth surface it is placed on.
		ball_offset = dedent_sphere_dimeter / 2 - dedent_sphere_offset;
		
		translate([pos(pos), 0, 0]) {
			scale([dir(pos), 1, 1]) {
				intersection() {
					translate([ball_offset, 0, 0]) {
						sphere(d = dedent_sphere_dimeter);
					}
					
					// Needs to be slightly past 0.1 because otherwise the final shape will have infinitely thin gaps.
					sector_3d(xmax = 0.1);
				}
			}
		}
	}
		
	module dedent_hole(pos) {
		translate([pos(pos), 0, 0]) {
			rotate([0, dir(pos) * 90, 0]) {
				cylinder(h = dedent_sphere_offset, d1 = dedent_hole_diameter, d2 = dedent_hole_diameter - 2 * dedent_sphere_offset);
			}
		}
	}
	
	// The part to cut away inside the corner clearance so that two parts can join and rotate.
	module clearance_chamfer() {
		sector_3d(ymax = gap / 2);
		
		// To allow rotating two joined parts.
		rotate([90 - min_angle / 2, 0, 0]) {
			sector_3d(ymax = gap / 2);
		}
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
		sector_3d(ymax = thickness / 2 + gap);
		
		rotate([90 - min_angle, 0, 0]) {
			sector_3d(ymax = thickness / 2 + gap);
		}
	}
	
	// The volume which is occupied by the teeth.
	module teeth() {
		difference() {
			for (j = [0:num_teeth - 1]) {
				sector_3d(xmin = pos(2 * j), xmax = pos(2 * j + 1));
			}
			
			dedent_hole(2);
			dedent_hole(5);
		}
		
		dedent_ball(1);
		dedent_ball(4);
	}
	
	difference() {
		union() {
			intersection() {
				trace(true) edge();
				sector_3d(zmin = -thickness / 2, zmax = thickness / 2);
			}
			
			trace() intersection() {
				teeth_cylinder();
				teeth();
			}
		}
		
		trace() difference() {
			intersection() {
				teeth_chamfer();
				edge_region();
			}
			
			clearance_region();
			teeth();
		}
		
		trace() intersection() {
			clearance_chamfer();
			clearance_region();
		}
		
		trace(true) edge(loop_width);
	}
}

module regular_fillygon(num_sides) {
	fillygon([for (_ = [1:num_sides]) 180 - 360 / num_sides]);
}
