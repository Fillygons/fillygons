include <../_fillygon.scad>

render() {
	translate([0, side_length, 0]) {
		rotate([min_angle - 180, 0, 0]) {
			regular_fillygon(4);
		}
	}
	
	rotate([0, 0, 90]) {
		regular_fillygon(3);
	}
	
	regular_fillygon(4);
	
	translate([side_length, side_length, 0]) {
		rotate([0, 0, -90]) {
			regular_fillygon(5);
		}
	}
	
	rotate([min_angle, 0, 0]) {
		translate([0, -side_length, 0]) {
			regular_fillygon(4);
		}
	}
}
