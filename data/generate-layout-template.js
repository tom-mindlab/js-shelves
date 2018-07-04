/*
	Rules of the game
*/

const
	_ = require('lodash'),
	fs = require('fs')
	generateLayouts = require('../src/generateLayouts'),
	pytools = require('../src/pytools')


const saveJSON = (object, path)=> {
	fs.writeFileSync(path, JSON.stringify(object, null, 2))
}

const market = 'ghana'

const output_folder = './' + market


// configuration
const configuration = require(output_folder + '/setup.json')

// output
const layout_template_file = output_folder + '/layout-template.json'


// Generate a layout template
generateLayouts(configuration)
	.then(layout => {
		saveJSON(layout,layout_template_file)
	})


