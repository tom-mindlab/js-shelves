const 
	_ = require('lodash'),
	fs = require('fs'),
	path = require('path'),
	pytools = require('../src/pytools')

const root_folder = __dirname
const market = 'ethiopia'

const output_folder = path.join(root_folder, market)

// Load the layout template for this market
const layout_template_file = output_folder + '/layout-template.json'
const layout  = require(layout_template_file)


const fs_stub = 'C:\\Users\\Joe\\Desktop\\Fix the shelves\\Shelves\\shelf-generator\\data\\'
const url_stub = 'http://toosuite-public-resources.s3.amazonaws.com/Diageo%20-%20Guinness%20Malta/Shelves/'



// Read in the test images
var files = fs.readdirSync('./test_images')
//files = files.slice(0,3)

const replacements = _.map(files, f=> {

	return {
		folder : f.replace('.png',''),
		image_path : './test_images/' + f
	}

})


/*
	Replace all the configs
*/
var needs_generating = []
_.each(replacements, test => {

	const test_folder = path.join(output_folder, test.folder)

	if(!fs.existsSync(test_folder)){
		fs.mkdirSync(test_folder);
	}

	// rewrite the layout
	const variant = JSON.parse(JSON.stringify(layout))

	variant.layouts = _.map(variant.layouts, l=> {

		if(l.image=='./test_images/MaltaCurrent1.png'){
			l.image = test.image_path
		}
		
		return l

	})

	const slayout_file = path.join(test_folder, 'layout.json')

	fs.writeFileSync(slayout_file, JSON.stringify(variant, null, 2))


	needs_generating.push({
		folder : test_folder,
		layout_file : slayout_file
	})

})


const getNameFromPath = str => {
	str = str.substring(str.lastIndexOf("/") + 1, str.length);
	return str.replace('.png','')
}


/*
	Get the target rectange for a particular row
*/
const getRectangeForRow = row => {
	return [{
		x1 : row.x_position,
		y1 : row.y_position,
		x2 : row.x_position + row.width,
		y2 : row.y_position + row.height
	}]
}


const fixFolder = folder => {
	return folder.replace(fs_stub, url_stub).replace(/\\/g,'/')
}


_.each(needs_generating, ng=> {

	const ly = require(ng.layout_file).layouts
	const folder = ng.folder
	var bases = _.uniq(_.map(ly,'base'))
	

	/*
		Generate flicker
	*/
	var configuration = []

	_.each(bases, b=> {

		var next_item = {
			name : "base_" + b,
			mainImage : {
				path : fixFolder(folder) + '/base_' + b + '.jpg'
			} 
		}

		// subset the layout to get the different variants
		var sub_layouts = _.filter(ly, l=> l.base==b && l.test)

		var targets = []
		_.each(sub_layouts, (sl, ix)=> {

			targets.push({
				name : 'variant_' + b + '_' + sl.index + '_' + getNameFromPath(sl.image),
				image : {
					path : fixFolder(folder) + '/variants/variant_' + b + '_' + sl.index + '.jpg'
				},
				rectangle : getRectangeForRow(sl)
			})
		})

		next_item.targets = targets

		configuration.push(next_item)

	})

	// save the flicker config
	fs.writeFileSync(folder + '/flicker.json', JSON.stringify(configuration, null, 2))


	/*
		Generate visual search
	*/
	var configuration = {
		name : 'visual_search_all_images'
	}

	var targets = []
	_.each(bases, b=> {
		// subset the layout to get the different variants
		var sub_layouts = _.filter(ly, l=> l.base==b && l.test)
		
		var products = _.uniq(_.map(sub_layouts, 'image'))

		_.each(products, p=> {

			var matching = _.filter(sub_layouts, sl=> sl.image==p)

			var x_min = _.minBy(matching, 'x_position').x_position
			// all have the same width
			var x_max = _.maxBy(matching, 'x_position').x_position + matching[0].width

			targets.push({
				image : {
					path : fixFolder(folder) + '/base_' + b + '.jpg'
				},
				name : "base_" + b + '_' + getNameFromPath(matching[0].image),
				text : "Please find and click on the following product: " + getNameFromPath(matching[0].image),
				rectangle :  [{
					x1 : x_min,
					y1 : matching[0].y_position,
					x2 : x_max,
					y2 : matching[0].y_position + matching[0].height
				}]
			})


		})


	})

	configuration.targets = targets
	configuration = [configuration]

	// save the flicker config
	fs.writeFileSync(folder + '/visual-search.json', JSON.stringify(configuration, null, 2))


})




/*
	Create the shelves
*/
_.each(needs_generating, ng=> {
	pytools.generateShelves(ng.layout_file, ng.folder)
})





