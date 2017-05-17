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

// Return a list of all integers not smaller than start but smaller than end. The start can be omitted and defaults to 0.
function range(start, end) = end == undef ? range(0, start) : (start < end ? [start:end - 1] : []);

// Return a list of elements from positions range(start, end) in list v.
function slice(v, start, end) = [for (i = range(start, end)) v[i]];

// Return the sum of the elements of list v.
function sum_list(v, i = 0) = i < len(v) ? v[i] + sum_list(v, i + 1) : 0;

// Return a new list, where each element is the sum of the element up to the element at the same position in list v.
function accumulate_list(v) = [for (i = range(len(v))) sum_list(slice(v, 0, i + 1))];

// Compute the linear combination of the vectors in v with the scalars from s.
function linear_combination(s, v) = sum_list([for (i = range(len(s))) s[i] * v[i]], iv = [0,0]);
