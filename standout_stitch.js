var fs = require('fs'),
	_ = require('underscore')

var data = JSON.parse(fs.readFileSync('./configuration_fl_Both.json'))
var data2 = JSON.parse(fs.readFileSync('./configuration_fl_Delight.json'))
var data3 = JSON.parse(fs.readFileSync('./configuration_fl_OIC.json'))
// var data4 = JSON.parse(fs.readFileSync('./standout_upsampled4.json'))

var newConfig = []
// Loop base
_.each(data, function(d){

	var targets = d.targets
	var newTargets = []




	_.each(targets, function(t){
			newTargets.push(t)
	})
	var next = {
		name : d.name,
		mainImage : d.mainImage
	}
	next.targets = newTargets
	newConfig.push(next)

})


_.each(data2, function(d){

	var targets = d.targets
	var newTargets = []




	_.each(targets, function(t){
			newTargets.push(t)
	})
	var next = {
		name : d.name,
		mainImage : d.mainImage
	}
	next.targets = newTargets
	newConfig.push(next)

})


_.each(data3, function(d){

	var targets = d.targets
	var newTargets = []




	_.each(targets, function(t){
			newTargets.push(t)
	})
	var next = {
		name : d.name,
		mainImage : d.mainImage
	}
	next.targets = newTargets
	newConfig.push(next)

})
/*
_.each(data4, function(d){

	var targets = d.targets
	var newTargets = []




	_.each(targets, function(t){
			newTargets.push(t)
	})
	var next = {
		name : d.name,
		mainImage : d.mainImage
	}
	next.targets = newTargets
	newConfig.push(next)

})

*/
fs.writeFileSync('./standout_Together.json', JSON.stringify(newConfig, null ,2))
