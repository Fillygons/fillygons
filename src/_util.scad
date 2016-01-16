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

function sum_list(v, i = 0) = i < len(v) ? v[i] + sum_list(v, i + 1) : 0;
