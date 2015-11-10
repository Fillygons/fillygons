include <_fillygon.scad>

render() {
	regular_fillygon(3);
	
	rotate([180 - acos(1 / 3), 0, 0]) {
		rotate([0, 0, -60]) {
			regular_fillygon(3);
		}
	}
	
	rotate([0, 0, 60]) {
		rotate([acos(1 / 3) - 180, 0, 0]) {
			regular_fillygon(3);
		}
	}
}
