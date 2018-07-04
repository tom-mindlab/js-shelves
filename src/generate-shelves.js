async function shelfStitcher() {
	$.getJSON("./shelves/shelf_types.json", function(shelf_types) {
		$.getJSON("./data/shelf_test/shelf_layout.json", function(shelf_layout) {
			console.log(shelf_layout);
		});
	});
}

class Item {
	constructor(json_item_obj) {
		this.name = json_item_obj.name;
		this.image_source = json_item_obj.URI;
	}
}

class Product extends Item {
	constructor(json_product_obj) {
		super(json_product_obj.name, json_product_obj.URI);
	}
}

const OVERFLOW_CALLBACKS = {
	SQUASH: function() {},
	OVERWRITE: {
		LEFT: function() {},
		RIGHT: function() {}
	},
	FAIL: function() {}
};

class Shelf extends Item {
	constructor(json_shelf_obj, json_shelf_types_map, overflow_callback) {
		super(json_shelf_obj.name, json_shelf_types_map[json_shelf_obj.type] + ".png");
		this.overflow_callback = overflow_callback;
		this.percentage_width = json_shelf_obj.percent_width;
	}

	pop() {
		this.products.pop();
	}

	push(item) {
		if (!(item instanceof Item)) {
			throw new TypeError("Shelf push expects Item object argument");
		} else {
			// TODO:
			// 1.   check if we have room for another product (width measurement), invoke overflow callback if there's no room
			// 1.1  this could potentially be deferred until rendering
			this.products.push(item);
		}
	}
}

class ShelfRack {
	constructor(json_shelves_arr) {
		if (!Array.isArray(json_shelves_arr)) {
			throw new TypeError("ShelfRack must be constructed with array");
		} else if (json_shelves_arr.length > 0) {
			for (let s of json_shelves_arr) {
				if (!(s instanceof Shelf)) {
					throw new TypeError("ShelfRack array must consist only of Shelf objects");
				}
			}
		} else {
			this.shelves = json_shelves_arr;
		}
	}

	// fill shelves with images
	populateShelves() {}
}

// entry
$(document).ready(function() {
	$("#main").append('<img src="./shelves/SINGLE_SHELF.png" width="50%"/>');
	$("#main").append('<img src="./shelves/SINGLE_SHELF.png" width="50%"/>');

	$.getJSON("./shelves/shelf_types.json", function(shelf_types) {
		$.getJSON("./data/shelf_test/shelf_layout.json", function(shelf_layout) {
			let S = new Shelf(shelf_layout.shelves[0], shelf_types.shelf_types, OVERFLOW_CALLBACKS.FAIL);
		});
	});
});
