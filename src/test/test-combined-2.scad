include <../_fillygon.scad>

render() {
	rotate([0, 50 - 180, 0]) {
		rotate([0, 0, 90]) {
			regular_fillygon(3);
		}
	}
	
	regular_fillygon(4);
}
