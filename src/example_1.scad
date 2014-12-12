include <_settings.scad>

render(convexity = 10) {
	linear_extrude(plate_height)
		import("example.dxf", layer = "text");
}
