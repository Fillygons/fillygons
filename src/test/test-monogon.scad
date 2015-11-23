include <../_fillygon.scad>

render() intersection() {
	translate([0, -15, -15]) cube(side_length);
	fillygon([]);
}
