AngularJS Attributes Completion
===

**Supports Sublime Text 2 and Sublime Text 3**

Installation Options
---

* Install this plug-in via [Sublime Package Control](http://wbond.net/sublime_packages/package_control)

* [Download](https://github.com/subhaze/angularjs-attributes/archive/master.zip) this repo and rename it to `AngularJS Attributes Completion` and place it within your `Packages` folder. This can be found within Sublime Text at `Preferences > Browse Packages…`

* Clone the repo into your `Packages` folder ` git clone git://github.com/subhaze/angularjs-attributes.git "AngularJS Attributes Completion"`

Plug-in Details
---
This plug-in allows for auto-completion of core AngularJS attributes, such as `ng-repeat` or `ng-click` within HTML elements.

Extending The Plugin
---

You can extend this plug-in with your own custom attributes that you've created by
adding them to the `extended_attribute_list` property in the User settings.

**Example** *add within 'Settings - User'*

```json
{
	"extended_attribute_list":[
		["my-directive\tMy Directives", "my-directive=\"${1:string}\"$0"],
	]
}
```

You can also override the `core_attribute_list` by setting that property within the User settings as well.

**Taking things one step further**

You can also define custom components that you've created in AngularJS by adding them to the `angular_components`. By default there are no components added to the list.

You can add some like so:

```json
{
	"angular_components":[
		"componentone",
		"componenttwo"
	]
}
```

Simply start by typing an agle bracket `<` and then your elements will appear within the completion list.
