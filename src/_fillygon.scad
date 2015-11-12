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
		
		ball(1);
		ball(4);
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
		
		hole(2);
		hole(5);
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
		sector_3d(xmin = 0, xmax = corner_clearance + gap / 2);
		sector_3d(xmin = side_length - corner_clearance + gap / 2, xmax = side_length);
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
				xmin = pos(2 * j) + gap / 2;
				xmax = pos(2 * j + 1) - gap / 2;
				
				sector_3d(xmin = xmin, xmax = xmax);
			}
			
			dedent_holes();
		}
		
		dedent_balls();
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
