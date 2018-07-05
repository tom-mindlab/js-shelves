async function shelfStitcher() {
	$.getJSON("./shelves/shelf_types.json", function(shelf_types) {
		$.getJSON("./data/shelf_test/shelf_layout.json", function(shelf_layout) {
			console.log(shelf_layout);
		});
	});
}

class Item {
	constructor(name, URI) {
		this.name = name;
		this.image_source = URI;
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
	constructor(json_shelf_obj, overflow_callback) {
		super(json_shelf_obj.name, json_shelf_obj.name);
		this.overflow_callback = overflow_callback;
		this.percentage_width = json_shelf_obj.percent_width;
		this.products = [];
	}

	pop() {
		this.products.pop();
	}

	push(item) {
		if (!(item instanceof Item)) {
			throw new TypeError("Shelf push method expects Item object argument");
		} else {
			// TODO:
			// 1.   check if we have room for another product (width measurement), invoke overflow callback if there's no room
			// 1.1  this could potentially be deferred until rendering
			this.products.push(item);
		}
	}
}

class ShelfRack {
	constructor(shelves_arr) {
		if (!Array.isArray(shelves_arr)) {
			throw new TypeError("ShelfRack must be constructed with array");
		} else if (shelves_arr.length > 0) {
			for (let s of shelves_arr) {
				if (!(s instanceof Shelf)) {
					throw new TypeError("ShelfRack array must consist only of Shelf objects");
				}
			}
			this.shelves = shelves_arr;
		}
	}
}

function parseItems(json_obj, item_arr) {
	if (!Array.isArray(item_arr)) {
		throw new TypeError("parseItems requires an array-type object to build against");
	}
	if (Array.isArray(json_obj)) {
		for (let i = 0; i < json_obj.length; ++i) {
			item_arr = parseItems(json_obj[i], item_arr);
		}
	} else {
		if (json_obj.type === "shelf") {
			item_arr.push(new Shelf(json_obj, OVERFLOW_CALLBACKS.FAIL));
		} else if (json_obj.type === "product") {
			item_arr.push(new Product(json_obj));
		} else {
			throw new Error('parsed json object with invalid "type" property: ' + json_obj.type);
		}
		// here we scan for nested items
		for (let key in json_obj) {
			if (Array.isArray(json_obj[key])) {
				item_arr[item_arr.length - 1].products = parseItems(json_obj[key], item_arr[item_arr.length - 1].products);
			}
		}
	}
	return item_arr;
}

// entry
$(document).ready(function() {
	$.getJSON("./shelves/shelf_types.json", function(shelf_types) {
		$.getJSON("./data/shelf_test/shelf_layout.json", function(shelf_layout) {
			let R = new ShelfRack(parseItems(shelf_layout.items, new Array()));
		});
	});
});
