_inf = 1e4;
_inf2 = 2 * _inf;

module extrude(min = -_inf, max = _inf) {
	translate([0, 0, min]) {
		linear_extrude(max - min) {
			children();
		}
	}
}

module sector_2d(xmin = -_inf, xmax = _inf, ymin = -_inf, ymax = _inf) {
	translate([xmin, ymin]) {
		square([xmax - xmin, ymax - ymin]);
	}
}

module sector_3d(xmin = -_inf, xmax = _inf, ymin = -_inf, ymax = _inf, zmin = -_inf, zmax = _inf) {
	translate([xmin, ymin, zmin]) {
		cube([xmax - xmin, ymax - ymin, zmax - zmin]);
	}
}

module inverse_minkowski_2d() {
	difference() {
		square(_inf, center = true);
		
		minkowski() {
			children(0);
			
			difference() {
				square(_inf2, center = true);
				children(1);
			}
		}
	}
}
