const
	_ = require('lodash'),
	pytools = require('./pytools'),
	shelves_info = require('../shelves/shelf_data.json')





/*
	Utility function for weighted sampling
*/
const sampleWeighted = weights => {

	// use weighted sampling
	var total = 0
	var cumulative_totals = []
	_.each(weights, wt=> {
		total+=wt
		cumulative_totals.push(total)
	})


	const random_value = Math.random()*total
	const selected_index = _.findIndex(cumulative_totals, t => t > random_value)
	
	return selected_index

}





/*
	Select products to put on a shelf
	using the available space the required number of products (min, max) and weights.

	This is the rules of the game. 
	Make different stackers for different rules
*/

class HorizontalStacker {

	constructor(skus){
		this.skus = skus
	}


	getRequired(){

		const required_skus = _.filter(this.skus, s=> s.required)

		var required_items = []

		_.each(required_skus, ri => {
			required_items = required_items.concat(ri.selectItems())
		})

		return required_items

	}

	// want to be able to blacklist items that are already on another shelf
	selectNext(max_width, blacklist){

		// select the items that can actually fit
		const skus_that_fit = _.filter(this.skus, s=> 
			!_.includes(blacklist, s.name) &&
			s.canSelect(max_width) && 
			(s.getNextSelectionWidth() < max_width)
		)

		if(_.isEmpty(skus_that_fit)) return null


		// get an array of the weights of these skus
		const weights = _.map(skus_that_fit, s => s.getNextSelectionWeight())

		// perform a weighted sampling for the index
		const sku_index = sampleWeighted(weights)

		// grab the selected sku
		const selected_sku = skus_that_fit[sku_index]

		const selected = selected_sku.selectItems()

		return selected

	}

}










/*
	Contains basic information about a shelf unit
*/

class SKU {

	/*
		currently the description should contain the following variables
		width, weight (optional), min_items, max_items		
	*/
	constructor(description){

		this.name      = description.name
		this.required  = description.required || false
		this.min_items = description.min_items || 1
		this.max_items = description.max_items || this.min_items
		this.weight    = description.weight || 1
		this.width     = description.width
		this.height    = description.height
		this.test      = description.test || false
		this.scale     = description.scale

		if(!this.width) throw new Error('sku "' + this.name + '" does not have width')
		
	}

	getNextSelectionCount(){
		return this.min_items
	}

	canSelect(){
		return this.getNextSelectionCount() > 0
	}

	getNextSelectionWidth(){
		return this.width * this.min_items
	}

	getNextSelectionWeight(){
		return this.weight * this.min_items
	}

	getItem(){
		return {
			name   : this.name,
			width  : this.width,
			test   : this.test,
			scale  : this.scale,
			height : this.height
		}
	}

	selectItems(){

		const min_items = this.min_items
		if(min_items==0) throw new Error('cannot select item - no more left')

		var selected = []
		for(var i=0 ; i<min_items ;i++){
			selected.push(this.getItem())
		}

		if(min_items < this.max_items){
			this.min_items = 1
			this.max_items = this.max_items - min_items
		} else {
			this.min_items = 0
			this.max_items = 0
		}

		this.required = false // no longer required if it was

		return selected

	}


}




/*
	Keeps track of the product added to the shelf
*/

class Shelf {


	constructor(configuration){

		this.width = configuration.width // assuming all shelves are the same width
		this.shelf_count = configuration.count 

		this.shelf_indexes = _.range(0, this.shelf_count)

		// initialise each shelf with empty array
		this.shelves = _.map(this.shelf_indexes, ()=> [] )

	}


	addItems(items, shelf_idx){
	
		if(!_.isArray(items)){
			items = [items]
		}

		this.shelves[shelf_idx] = this.shelves[shelf_idx].concat(items)

	}


	/*
		Returns the total width of the items on the shelf
	*/
	getItemsWidth(shelf_idx){

		var total_width = 0
		_.each(this.shelves[shelf_idx], c=> {
			total_width += c.width
		})
		return total_width

	}


	getRemainingWidth(shelf_idx){
		return this.width - this.getItemsWidth(shelf_idx)
	}

	/*
		Calculate which shelves have space for a particular width
	*/
	getShelvesWithSpace(required_width){

		var shelves_with_space = []

		_.each(this.shelf_indexes, si=> {
			if(this.getRemainingWidth(si) > required_width){
				shelves_with_space.push(si)
			}
		})

		return shelves_with_space

	}


	getProductsOnShelf(shelf_idx){
		return _.uniq(_.map(this.shelves[shelf_idx],'name'))	
	}

	getProductsOnOtherShelves(shelf_idx){
		var other_products = []
		_.each(this.shelf_indexes, si=> {
			if(si==shelf_idx) return
			other_products = other_products.concat(this.getProductsOnShelf(si))
		})

		return other_products
	}


	stack(stacker){

		/*
			Step 1. Assign the required items to random shelves
		*/
		const required_items = stacker.getRequired()

		// calculate the width required for each of the required items
		const unique_names = _.shuffle(_.uniq(_.map(required_items, 'name')))

		// loop through the randomised names assigning to a shelf
		_.each(unique_names, nm=> {

			// calculate the width of the items
			const items = _.filter(required_items, ri => ri.name==nm)
			const required_width = _.reduce(items, (sum, it)=> {
				return sum + it.width
			}, 0)

			var shelf_idxs = this.getShelvesWithSpace(required_width)

			if(_.isEmpty(shelf_idxs)) throw new Error('cannot accomodate required items')

			var selected_idx = _.sample(shelf_idxs)

			this.addItems(items, selected_idx)

		})


		/*
			Step 2. Assign random items to each shelf
		*/

		var keep_stacking = true
		while(keep_stacking){

			var cannot_continue = true
			_.each(this.shelf_indexes, si=> {

				// build a blacklist
				const black_list = this.getProductsOnOtherShelves(si)

				var next_items = stacker.selectNext(this.getRemainingWidth(si), black_list)

				if(next_items){
					this.addItems(next_items, si)
					cannot_continue = false
				}

			})

			keep_stacking = !cannot_continue

		}

	}

}







/*
	Actually generate the layouts
*/
const generateLayouts = async configuration => {


	var { items, prop_shelf_height } = configuration

	const shelf_info = shelves_info[configuration.shelf_id]

	// info about the individual images
	const image_info = await pytools.getImageInfo(_.map(items, 'image'))
	
	// target image height
	const target_height = shelf_info.shelf_height * prop_shelf_height


	// number and width of shelves
	const shelf_width = _.maxBy(shelf_info.shelf_coordinates,'width').width
	const shelf_count = shelf_info.shelf_count

	// attach the target width to each image
	items = _.map(items, it => {

		const info = image_info[it.image]

		it.name  = it.image // just give it the same names as the image path
		it.scale = target_height / info.height
		it.width = info.width * it.scale
		it.height = target_height

		return it
	})

	const shelves = []

	// Populate the shelves
	for(var b_idx=0 ; b_idx < configuration.layout_count ; b_idx++){

		const SKUs = _.map(items, item => new SKU(item))
		const hs = new HorizontalStacker(SKUs)
		const shelf = new Shelf({
			width : shelf_width *.9,
			count : shelf_count 
		})

		shelf.stack(hs) // we now have the products that can fit


		// next step we need to perform a grouping
		// for now lets just do the crudest possible grouping by products
		
		var index = 0 // get track of the overall index
		var layout_array = []
		_.each(shelf.shelves, (shelf_arr, idx) => {

			// get the shelf info
			const coords = shelf_info.shelf_coordinates[idx]

			// randomise the names
			const names = _.shuffle(_.uniq(_.map(shelf_arr, 'name')))
			
			// apply the randomisation to the items
			shelf_arr = _.sortBy(shelf_arr, c=> names.indexOf(c.name))

			// TODO - move ton configuration
			const MARGIN = 4

			// calculate the length of the shelf array
			var taken_shelf_width = _.reduce(shelf_arr, (sum, item)=> {
				return sum += item.width
			}, 0) 
			taken_shelf_width += MARGIN * (shelf_arr.length -1)

			var current_x = (shelf_width - taken_shelf_width) / 2 
			
			// todo: here we could calculate the positions
			_.each(shelf_arr, (c, c_idx)=> {

				layout_array.push({
					image : c.name,
					scale : c.scale,
					test  : c.test,
					base  : b_idx,
					index : index++,
					shelf_index : idx,
					shelf_item_index : c_idx,
					x_position : Math.round(current_x), // python expects integers
					y_position : Math.round(coords.bottom - target_height), // "
					width : Math.round(c.width),
					height : c.height
				})

				current_x += (c.width + MARGIN)
			})

		})

		shelves.push(layout_array)

	}


	// concatenate all items for the shelf generator
	var all_items = []
	_.each(shelves, sh=> {
		all_items = all_items.concat(sh)
	})



	return {
		configuration : {
			// these defaults should be elsewhere
			generate_variants : configuration.flicker || true, // default to generating flicker variant
			blur_radius       : configuration.blur_radius || 3,
			output_quality    : configuration.quality || .9
		},
		shelf : shelf_info,
		layouts : all_items
	}



}


module.exports = generateLayouts