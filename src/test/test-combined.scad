include <../_fillygon.scad>

render() {
	rotate([0, -60, 0]) {
		translate([-side_length, 0, 0]) {
			fillygon(angles = regular_angles(num_sides = 4, side_repetitions = 1), filled = true, filled_corners = true, gap = 0.4, min_concave_angle = 180, min_convex_angle = 90);
		}
	}
	
	fillygon(angles = regular_angles(num_sides = 4, side_repetitions = 1), filled = true, filled_corners = true, gap = 0.4, min_concave_angle = 180, min_convex_angle = 90);
	
	rotate([90, 0, 0]) {
		rotate([0, 0, -120]) {
			fillygon(angles = regular_angles(num_sides = 6, side_repetitions = 1), filled = true, filled_corners = true, gap = 0.4, min_concave_angle = 180, min_convex_angle = 90);
		}
	}
}
