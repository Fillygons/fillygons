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

// Length on each end of an edge ehere no teeht are placed.
corner_clearance = 8;

// Width of chamfers cut into the edges and resulting edges at corners to make them less sharp/pointy.
chamfer_height = 1;

// Overhang of the ball dedents relative to the teeth surface.
dedent_sphere_offset = 0.5;

// Diameter of the ball dedent spheres.
dedent_sphere_dimeter = thickness;

// Diameter of the holes which accept the ball dedent spheres.
dedent_hole_diameter = 2.0;

// With of the small, flexiple teeth.
small_tooth_width = 1.4;

// Gap between the small, flexiple teeth.
small_tooth_gap = 1;

// Depth to which to cut around the small, flexiple teeth.
small_teeth_cutting_depth = 5.5;

// With to cut around the small, flexiple teeth.
small_teeth_cutting_width = 0.6;

$fn = 8;

// Produces a single fillygon with n edges. The piece is oriented so that the outside of the polygon is on top.
// angles: A list of n - 1 numbers, specifying the interior angles.
// reversed_edges: A list of booleans, specifying on which edges to reverse the tenons. The passed list is padded to n elemens with the value false.
// filled: Specifies whether to close the inside of the polygon by filling in the lower side.
// filled_corners: Whether to cut a smaller bevel in the corners clearance region instead of using the same bevel as between the teeth.
// min_convex_angle: Minimum dihedral angle supported in a convex configuration.
// min_concave_angle: Minimum dihedral angle supported in a non-convex configuration.
module fillygon(angles, reversed_edges = [], filled = false, filled_corners = false, min_convex_angle = min_angle, min_concave_angle = min_angle, gap = 0.4) {
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
			// Ugly hack to pass the angle of the previous corner into the child modules.
			$corner_angle = all_angles[i];
			
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
	
	// Calculates the x-position of the chamfer for an edge produced by 2 planes with distance d from the origin and anges a1 and a2.
	function chamfer_pos(d, a1, a2) = (chamfer_height * (cos(a1 - a2) + cos(a1 + a2)) / 2 + d * (cos(a1) + cos(a2))) / sin(a1 + a2);
	
	// Calculates the x-position of the chamfer for a corner produced by 2 planes with distances d from the origin and internal angle a.
	function corner_chamfer_pos(d, a) = chamfer_pos(d, a / 2, a / 2);
	
	// Used for cutting a chamfer into the corners.
	num_corners = len(angles) + 1;
	all_angles = concat([180 * (num_corners - 2) - sum_list(angles)], angles);
	
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
	
	// The region spanning the whole ideal edge.
	module edge_region() {
		sector_3d(xmin = 0, xmax = side_length);
	}
	
	// The part that needs to be removed to support acute angles.
	module teeth_bevel() {
		offset = thickness / 2 + gap;
		
		// Top bevel.
		if (min_concave_angle < 90) {
			rotate([min_concave_angle - 90, 0, 0]) {
				sector_3d(ymax = offset);
			}
		}
		
		// Bottom bevel.
		if (min_convex_angle < 90) {
			rotate([90 - min_convex_angle, 0, 0]) {
				sector_3d(ymax = offset);
			}
		}
		
		// Position at which to place a chamfer when both sides are bevelled.
		chamfer_pos = chamfer_pos(offset, min_concave_angle, min_convex_angle);
		
		// Whether a chamfer is necessary.
		needs_chamfer = min_concave_angle < 90 && min_convex_angle < 90;
		
		// Either cut a chamfer or cut to allow for the cylinder parts of the teeth of the connected tile.
		edge_pos = needs_chamfer ? chamfer_pos : thickness / 2 + gap;
		
		// Edge chamfer.
		sector_3d(ymax = edge_pos);
		
		// Corner chamfer.
		rotate([0, 0, $corner_angle / 2]) {
			sector_3d(xmax = corner_chamfer_pos(edge_pos, $corner_angle));
		}
	}
	
	// The part that needs to be removed at the corners, if they are filled.
	module clearance_bevel() {
		offset = gap / 2;
		
		// Top bevel.
		rotate([min_concave_angle / 2 - 90, 0, 0]) {
			sector_3d(ymax = offset);
		}
		
		// Bottom bevel.
		rotate([90 - min_convex_angle / 2, 0, 0]) {
			sector_3d(ymax = offset);
		}
		
		// Position at which to place a chamfer, if both sides are bevelled.
		chamfer_pos = chamfer_pos(offset, min_concave_angle / 2, min_convex_angle / 2);
		
		// Edge chamfer.
		sector_3d(ymax = chamfer_pos);
		
		// Corner chamfer.
		rotate([0, 0, $corner_angle / 2]) {
			sector_3d(xmax = corner_chamfer_pos(chamfer_pos, $corner_angle));
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
				
				// The frame with beveled edges and cuttings. 
				trace(true) difference() {
					edge();
					
					// The chamfer region in the region of the teeth and corresponding gaps.
					difference() {
						teeth_bevel();
						
						if (filled_corners) {
							// Disable the teeth-region beveling inside the clearance.
							clearance_region();
						}
					}
					
					if (filled_corners) {
						// The beveling region of the teeth and corresponding gaps.
						intersection() {
							clearance_bevel();
							clearance_region();
						}
					}
					
					// Cut small gaps around the flexible teeth.
					dedent_cutting_region();
				}
			}
			
			// The actual teeth.
			trace() intersection() {
				// The shape of the teeth.
				union() {
					teeth_cylinder();
					intersection() {
						sector_3d(zmin = -thickness / 2, zmax = thickness / 2);
						teeth_bevel();
						edge();
					}
				}
				
				// The region occupied by the teeth.
				teeth_region();
			}
		}
		
		// Cut away parts of the teeth that reach into adjacent edges on acute corner angles.
		trace() intersection() {
			difference() {
				teeth_bevel();
				
				// Do not trim any parts that are part of a tooth an this edge (obviously).
				teeth_region();
				
				// Do not trim the teeth from adjacent edges outside of the region of the teeth end corrensponding gaps.
				clearance_region();
			}
			
			edge_region();
		}
		
		// Cut out the inside of the loop.
		trace(true) intersection() {
			edge(loop_width);
			
			if (filled) {
				// Prevents a thin layer form being cut away, closing the tile's face.
				sector_3d(zmin = filling_height - thickness / 2);
			}
		}
	}
}

module regular_fillygon(num_sides, side_repetitions = 1, reversed_edges = [], filled = false, gap = 0.4) {
	dirs = [for (i = [1:num_sides]) for (j = [1:side_repetitions]) 360 / num_sides * i];
	angles = [for (i = [1:len(dirs) - 1]) 180 - dirs[i] + dirs[i - 1]];
	
	fillygon(angles, reversed_edges = reversed_edges, filled = filled, gap = gap);
}
