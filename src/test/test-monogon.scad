use <../_fillygon.scad>

render() intersection() {
	translate([0, -15, -15]) cube(30);
	fillygon([]);
}
