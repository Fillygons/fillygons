module extrude_layer(layer, height) {
	linear_extrude(height = height)
		import("example.dxf", layer = layer);
}

render(convexity = 10) {
	union() {
		difference() {
			extrude_layer("base", 2);
			
			translate([0, 0, -1e6])
				extrude_layer("text", 2e6);
		}
		
		extrude_layer("struts", 1);
	}
}
