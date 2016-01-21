include <../_fillygon.scad>

module place(index) {
	translate([index * 40, 0, 0]) {
		children();
	}
	
	translate([index * 40, -20, 0]) {
		rotate([180, 0, 0]) {
			children();
		}
	}
}

render() {
	place(0) regular_fillygon(3, filled_corners = false);
	place(1) regular_fillygon(3, filled_corners = false, min_concave_angle = 90);
	place(2) regular_fillygon(3, filled_corners = true, min_concave_angle = 90);
	place(3) regular_fillygon(3, filled_corners = true, min_concave_angle = 180);
	place(4) regular_fillygon(3, filled_corners = true, min_concave_angle = 180, min_convex_angle = 180);
}
