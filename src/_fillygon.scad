include <_util.scad>

// Thickness of the pieces.
thickness = 4;

// Width of the rim along the edges of the piece connecting the teeth.
loop_width = 2 * thickness;

// Heigth up to which to to fill the inside of the loop.
filling_height = 1;

// Length of a pieces sides, measured along the ideal polygon's edges.
side_length = 40;

// Minimum dihedral alnge between this face and any other face.
min_angle = 38;

// Length on each end of an edge ehere no teeht are placed..
corner_clearance = 8;

// Overhang of the ball dedents relative to the teeth surface.
dedent_sphere_offset = 0.5;

// Diameter of the ball dedent spheres.
dedent_sphere_dimeter = thickness;

// Diameter of the holes which accept the ball dedent spheres.
dedent_hole_diameter = 2;

// With of the small, flexiple teeth.
small_tooth_width = 1.4;

// Gap between the small, flexiple teeth.
small_tooth_gap = 1;

// Depth to which to cut around the small, flexiple teeth.
small_teeth_cutting_depth = 5.5;

// With to cut around the small, flexiple teeth.
small_teeth_cutting_width = 0.6;

// Gap between touching surfaces.
gap = 0.4;

$fn = 32;

module fillygon(angles, reversed_edges = []) {
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
			module reverse() {
				if (i < len(reversed_edges) && reversed_edges[i]) {
					translate([side_length / 2, 0, 0]) {
						scale([-1, 1, 1]) {
							translate([-side_length / 2, 0, 0]) {
								children();
							}
						}
					}
				} else {
					children();
				}
			}
			
			if (intersect) {
				intersection() {
					reverse() {
						children();
					}
					
					more(i) {
						children();
					}
				}
			} else {
				union() {
					reverse() {
						children();
					}
					
					more(i) {
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
	
	used_width = side_length - 2 * corner_clearance;
	small_teeth_width = 2 * small_tooth_width + small_tooth_gap;
	
	positions = [
		gap / 2,
		used_width / 4 - small_teeth_width / 2 - gap,
		used_width / 4 + small_teeth_width / 2 + gap,
		used_width / 2 - gap / 2,
		used_width * 3 / 4 - small_teeth_width / 2,
		used_width * 3 / 4 - small_tooth_gap / 2,
		used_width * 3 / 4 + small_tooth_gap / 2,
		used_width * 3 / 4 + small_teeth_width / 2,
		used_width + gap / 2];
	
	function dir(pos) = 1 - pos % 2 * 2;
	function pos(pos) = corner_clearance + positions[pos];
	
	// The infintely extruded region of the polygon with an optional offset.
	module edge(offset = 0) {
		sector_3d(ymin = offset);
	}
	
	// Translate and possibly mirror an object to position it at the specified position.
	module at_position(pos) {
		translate([pos(pos), 0, 0]) {
			scale([dir(pos), 1, 1]) {
				children();
			}
		}
	}
	
	// The cylinder which form part of the teeth.
	module teeth_cylinder() {
		rotate([0, 90, 0]) {
			extrude() {
				circle(d = thickness);
			}
		}
	}
	
	module clearance_region() {
		sector_3d(xmin = 0, xmax = pos(0));
		sector_3d(xmin = pos(len(positions) - 1), xmax = side_length);
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
		
		at_position(pos) {
			intersection() {
				translate([ball_offset, 0, 0]) {
					sphere(d = dedent_sphere_dimeter);
				}
				
				// The ball needs to extend slightly past the origin because otherwise the final shape will have infinitely thin gaps.
				sector_3d(xmax = 0.1);
			}
		}
	}
	
	// The volume to remove from the teeth to create the hole for a ball dedent on a tooth at the specified position.
	module dedent_hole(pos) {
		at_position(pos) {
			rotate([0, 90, 0]) {
				cylinder(h = dedent_sphere_offset, d1 = dedent_hole_diameter, d2 = dedent_hole_diameter - 2 * dedent_sphere_offset);
			}
		}
	}
	
	// A region to be cut out between teeth.
	module dedent_cutting(pos) {
		at_position(pos) {
			sector_3d(xmin = -small_teeth_cutting_width, xmax = 0, ymax = small_teeth_cutting_depth);
		}
	}
	
	// The volume which is occupied by the teeth. This includes the dedents and extends to infinity.
	module teeth_region() {
		difference() {
			for (j = [0:(len(positions) - 1) / 2]) {
				sector_3d(xmin = pos(2 * j), xmax = pos(2 * j + 1));
			}
			
			dedent_hole(1);
			dedent_hole(2);
		}
		
		dedent_ball(4);
		dedent_ball(7);
	}
	
	module dedent_cutting_region() {
		dedent_cutting(4);
		dedent_cutting(5);
		dedent_cutting(6);
		dedent_cutting(7);
	}
	
	difference() {
		union() {
			intersection() {
				// A thick plane with the thickness of the part.
				sector_3d(zmin = -thickness / 2, zmax = thickness / 2);
				
				// The region inside the chamfers and
				trace(true) difference() {
					edge();
					teeth_chamfer();
					dedent_cutting_region();
				}
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
		
		// Cut away parts of the teeth that reach into adjacent edges on acute corner angles.
		trace() intersection() {
			difference() {
				teeth_chamfer();
				teeth_region();
				clearance_region();
			}
			
			edge_region();
		}
		
		// Cut out the inside of the loop.
		trace(true) intersection() {
			edge(loop_width);
			sector_3d(zmin = filling_height - thickness / 2);
		}
	}
}

module regular_fillygon(num_sides, reversed_edges = [], side_repetitions = 1) {
	dirs = [for (i = [1:num_sides]) for (j = [1:side_repetitions]) 360 / num_sides * i];
	angles = [for (i = [1:len(dirs) - 1]) 180 - dirs[i] + dirs[i - 1]];
	
	fillygon(angles, reversed_edges);
}
