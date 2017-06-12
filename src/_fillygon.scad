include <_util.scad>

/**
Produces a single fillygon with n edges. The piece is oriented so that the outside of the polygon is on top.

Properties which change the overall shape without changing features necessary for compatibility between pieces:
    angles:
        A list of n numbers, specifying the interior angles.

    edges:
        A list of n numbers, specifying the side lengths.

    reversed_edges:
        A list of booleans, specifying on which edges to reverse the tenons. The passed list is padded to n elements with the value false.

    filled:
        Specifies whether to close the inside of the polygon by filling in the lower side.

    filled_corners:
        Whether to cut a smaller bevel in the corners clearance region instead of using the same bevel as between the teeth.

    min_convex_angle:
        Minimum dihedral angle supported in a convex configuration.

    min_concave_angle:
        Minimum dihedral angle supported in a non-convex configuration.

    gap:
        Gap to insert between parts touching between assembled pieces to make them fit well.

Properties which change non-functional parts of the piece:
    filling_height:
        Height up to which to fill the inside of the loop.

    loop_width:
        Width of the rim along the edges of the piece connecting the teeth.

    chamfer_height:
        Width of chamfers cut into the edges and resulting edges at corners to make them less sharp/pointy.

    fn:
        Number of sides per revolution used for rounded parts.

Properties which create incompatible pieces:
    thickness:
        Thickness of the pieces.

    side_length:
        Length of a pieces sides, measured along the ideal polygon's edges.

    dedent_sphere_offset:
        Overhang of the ball dedents relative to the teeth surface.

    dedent_sphere_diameter:
        Diameter of the ball dedent spheres.

    dedent_hole_diameter:
        Diameter of the holes which accept the ball dedent spheres.

    large_teeth_width:
        Width of the large teeth.

    small_teeth_width:
        Width of the small teeth.

    small_teeth_gap:
        Gap between the small, flexible teeth.

    small_teeth_cutting_depth:
        Depth to which to cut around the small, flexible teeth.

    small_teeth_cutting_width:
        Width to cut around the small, flexible teeth.
*/
module fillygon(angles, edges, reversed_edges, filled, filled_corners, min_convex_angle, min_concave_angle, gap, filling_height, loop_width, chamfer_height, fn, thickness, side_length, dedent_sphere_offset, dedent_sphere_diameter, dedent_hole_diameter, large_teeth_width, small_teeth_width, small_teeth_gap, small_teeth_cutting_depth, small_teeth_cutting_width) {
    $fn = fn;

	module reverse() {
		translate([$side_length / 2, 0, 0]) {
			scale([$reversed_edge ? -1 : 1, 1, 1]) {
				translate([-$side_length / 2, 0, 0]) {
					children();
				}
			}
		}
	}
	
	module trace(intersect = false) {
		module more(i) {
			if (i < len(angles) - 1) {
				translate([side_length_unit * edges[i], 0, 0]) {
					rotate(180 - angles[i + 1]) {
						tail(i + 1) {
							children();
						}
					}
				}
			}
		}
		
		module tail(i) {
			// Ugly hack to pass the angle of the previous corner into the child modules.
			$corner_angle = angles[i];
			$reversed_edge = i < len(reversed_edges) && reversed_edges[i];
			$side_length = side_length_unit * edges[i];

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
	
	// Calculates the x-position of the chamfer for an edge produced by 2 planes with distance d from the origin and angles a1 and a2.
	function chamfer_pos(d, a1, a2) = abs(a1 - 90) * PI / 180 < 1 / 1000 && abs(a2 - 90) * PI / 180 < 1 / 1000 ? d : (chamfer_height * (cos(a1 - a2) + cos(a1 + a2)) / 2 + d * (cos(a1) + cos(a2))) / sin(a1 + a2);
	
	// Calculates the x-position of the chamfer for a corner produced by 2 planes with distances d from the origin and internal angle a.
	function corner_chamfer_pos(d, a) = chamfer_pos(d, a / 2, a / 2);

	// These are, in order, the left and right edges of the first and second instance of the large and small teeth. The last element is the right end of the cutting which complements the first tooth. All elements are relative to the end of the left clearance region.
	positions = accumulate_list([
		0,
		large_teeth_width,
		2 * small_teeth_width + small_teeth_gap,
		large_teeth_width,
		large_teeth_width,
		small_teeth_width,
		small_teeth_gap,
		small_teeth_width,
		large_teeth_width]);

	// List which specifies, for each entry in the positions list, in which direction gap / 2 should be added, if at all.
	gaps = [1, -1, 1, -1, 1, 0, 0, -1, 1];

	// Length on each end of an edge where no teeth are placed.
	function corner_clearance(side_length) = (side_length - positions[len(positions) - 1]) / 2;

	function dir(pos) = 1 - pos % 2 * 2;
	function pos(pos, side_length) = corner_clearance(side_length) + positions[pos] + gaps[pos] * gap / 2;

	// The infinitely extruded region of the polygon with an optional offset.
	module edge(offset = 0) {
		sector_3d(ymin = offset);
	}
	
	// Translate and possibly mirror an object to position it at the specified position.
	module at_position(pos) {
		translate([pos(pos, $side_length), 0, 0]) {
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
		sector_3d(xmax = pos(0, $side_length));
		sector_3d(xmin = pos(len(positions) - 1, $side_length));
	}
	
	// The region spanning the whole ideal edge.
	module edge_region() {
		sector_3d(xmin = 0, xmax = $side_length);
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
		reverse() {
			rotate([0, 0, $corner_angle / 2]) {
				sector_3d(xmax = corner_chamfer_pos(edge_pos, $corner_angle));
			}
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
		reverse() {
			rotate([0, 0, $corner_angle / 2]) {
				sector_3d(xmax = corner_chamfer_pos(chamfer_pos, $corner_angle));
			}
		}
	}
	
	// The volume of a dedent ball placed on a tooth at the specified position.
	module dedent_ball(pos) {
		// Actual diameter used for the sphere, accounting for the gap.
		diameter = dedent_sphere_diameter - gap;
		
		// Offset of the sphere's center relative to the tooth surface it is placed on.
		ball_offset = diameter / 2 - dedent_sphere_offset;
		
		at_position(pos) {
			intersection() {
				translate([ball_offset, 0, 0]) {
					sphere(d = diameter);
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
				cylinder(h = dedent_sphere_offset, d = dedent_hole_diameter + gap / 2);
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
				sector_3d(xmin = pos(2 * j, $side_length), xmax = pos(2 * j + 1, $side_length));
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
				
				// Do not trim the teeth from adjacent edges outside of the region of the teeth end corresponding gaps.
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
