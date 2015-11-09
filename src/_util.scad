_inf = 1e6;
_inf2 = 2 * _inf;

rad = 180 / PI;

module infinite_extrude() {
	translate([0, 0, -_inf]) {
		linear_extrude(height = _inf2) {
			children(0);
		}
	}
}

module half_plane() {
	translate([0, _inf]) {
		square(_inf2, center = true);
	}
}

module half_space() {
	translate([0, 0, _inf]) {
		cube(_inf2, center = true);
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
