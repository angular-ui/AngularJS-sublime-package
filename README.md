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
This plug-in allows for auto-completion of core AngularJS attributes, such as `ng-repeat`, `ng-click`, etc… within HTML elements.

I've also tried hard at keeping this plug-in very extendable so that you may adjust things easily based on your own preferences. Often times in the past I've found my self having to make small tweaks to the source of a plugin like this making it very difficult to update while retaining my custom tweaks.

Extending The Attribute List
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


Extending With Custom Components
---

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

Now you can have auto-complete on your custom elements along with the normal HTML element list.


Extending Scopes
===

**Defining Tag Scopes**

By default this plugin will only allow attribute completions within the scope of an HTML tag or with a [Jade](https://github.com/davidrios/jade-tmbundle) attribute list.

This however can be changed by updating the property `attribute_defined_scopes`.

`attribute_defined_scopes` is just an array of scopes to check for to determine whether or not the attribute auto-completion should react. Below is the default settings for this property.

```json
{
	"attribute_defined_scopes": [
		"text.html meta.tag - text.html punctuation.definition.tag.begin",
		"constant.name.attribute.tag.jade"
	]
}
```

**Defining Component Scopes**

By default this plugin will only allow component completions within the source scope of HTML or [Jade](https://github.com/davidrios/jade-tmbundle). Just like the attribute scope this scope can be redefined as well, all you have to do is override the `component_defined_scopes` property which is also just an array of scopes. Below is the default settings for this property.

```json
{
	"component_defined_scopes": [
		"text.html - source",
		"source.jade"
	]
}
```

Strict Attribute Scope Matching
===

You can adjust the property `ensure_all_scopes_are_matched` to do strict matching on scopes (default is *false*). Meaning, all scopes that are defined must be matched otherwise the attribute list will not appear.

Adjusting this property with the default scope settings for attributes will basically turn this plugin completely off since it's looking for HTML tag scopes as well a [Jade](https://github.com/davidrios/jade-tmbundle) scopes.

In order for this option to be beneficial you must define your own attribute scopes to strict match on.