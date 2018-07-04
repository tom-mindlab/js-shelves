/*
	Utilities for calling the shelf generator code in python
*/

const
	child = require('child_process'),
	_  = require('lodash')



	

/*
	Generic python calling utility
*/
const runPython = args => {
	return new Promise((resolve, reject)=> {

		var python_process = child.spawn('python',args);
		python_process.stdout.on('data', data=> {
			resolve(data)
		})

		python_process.stderr.on('data', data=> {
			console.error(data.toString())
		})

		// TODO: rejection handling
	})
}


/*
	Get image info from python
*/
const getImageInfo = paths => {

	const path = __dirname + '/../python/getImageInfo.py'

	if(!_.isArray(paths)) paths = [paths]
	return runPython([path].concat(paths))
		.then(data => {
			return JSON.parse(data.toString())
		})
}



const generateShelves = (config_path, output_folder) => {

	const path = __dirname + '/../python/generateShelves.py'

	return runPython([path, config_path, output_folder])
		.then(data => {
			console.log(data.toString())
		})
}



/*
	Export all the useful functions
*/
module.exports = {
	getImageInfo, generateShelves
}