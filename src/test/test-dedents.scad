include <../_fillygon.scad>

render() {
	projection(cut = true) {
		fillygon([]);
		
		translate([side_length, 0, 0]) {
			rotate([0, 0, 180]) {
				fillygon([]);
			}
		}
	}
}
