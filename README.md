AngularJS Sublime Text Package (Beta)
===

**Supports Sublime Text 2 and Sublime Text 3**

This plugin is a work in progress but should be functional for usage. The main development platform is OSX with the latest builds of Sublime Text 3. 

Checks are made in Sublime Text 2 when adding/modifying features so things should work correctly for ST2.

Installation Options
---


* [Download](https://github.com/angular-ui/AngularJS-sublime-package/archive/master.zip) this repo and place it within your `Packages` folder. This can be found within Sublime Text at `Preferences > Browse Packages…`

* Clone the repo into your `Packages` folder ` git clone git://github.com/angular-ui/AngularJS-sublime-package.git`

Plug-in Details
---

**Completions**

Provides auto-completion of core AngularJS attributes, such as `ng-repeat`, `ng-click`, etc… within HTML and [Jade](https://github.com/davidrios/jade-tmbundle) elements.

![
](http://angular-ui.github.io/AngularJS-sublime-package/images/screenshot-directives-auto-complete.png)

You can also get completions for filters within HTML markup. Trigger the completions list via `ctrl+space` right after typing `|  ` (pipe plus a space) and you should find all your filters that have been indexed within the completion list.

![](http://angular-ui.github.io/AngularJS-sublime-package/images/screenshot-filters-auto-complete.png)

You're not limited to just HTML and [Jade](https://github.com/davidrios/jade-tmbundle) file types. You can extend the scope to allow for other templating languages. You can also add your own custom attributes and components for auto-completion.

**Goto Definition**

Once you have your project indexed you can use the keyboard shortcut `super+alt+ctrl+l` when your cursor is within directive/services/etc.. and you'll be trasported to the file that contains the definition. 

**Quick Panel Definition Look Ups**

Quickly find your directives/filters/modules/factories via the quick_panel. Once your project has been indexed, by either executing the command 'AngularJS: Rebuild Search Index' from the command palette or executing the shortcut `super+ctrl+l` to open the quick_panel search for the first time.

![](http://angular-ui.github.io/AngularJS-sublime-package/images/screenshot-quick_panel-search.png)

Each time you save a file that file will be reindexed, if you have already triggered indexing, so that the quick_panel search stays up-to-date.

The regex that's used for look up expects the definitions to start like one of the the following examples

```js
	filter('interpolate', ['version', function(version) {
```

```js
	.filter('interpolate', ['version', function(version) {
```

```js
	('chained').filter('interpolate', ['version', function(version) {
```

```js
	app.filter('interpolate', ['version', function(version) {
```

```js
	angular.module('myApp', [])
```

Tab Triggers
---

#### Html
* __repeat__
* __switch + when + default__
* __show + hide__
* __plural__ pluralize
* __options__
* __view__ 
* __inc__ include
* __click__

#### Javascript
* __is + [# to select]__ isArray, isObject, isDefined, isFunction, isString
* __lower__ lowercase
* __upper__ uppercase
* __mod + dir__ new module or directive template
* __noop__
* __extend__
* __each__ forEach
* __http__
* __watch__
* __digest__
* __el__ element
* __.$ + [# to select]__ $scope.$digest, $scope.$apply, $scope.$watch, $scope.$eval
* __http__ $http()
* __noop__
* __filter__ $filter
* __copy__
* __mod__ angular.module(). // Includes a preceeding docblock
* __dir__ directive()
* __route__ $routeProvider.when
* __toJson__ angular.toJson()
* __log__ $log.log()


Quick Panel Definition Look Up Options
---

**Excluding Folders** *(requires project to be re-indexed *)

You can exclude folders by adding them to the `exclude_dirs` property in the User Settings. By default 'node_modules/' is excluded, but you will need to add it back if you update the excluded_dirs property in your User Settings.

**Excluding Files By Suffix**

You can exclude files via their suffix by adding them to the `exclude_file_suffixes` list. By default, 'min.js' and 'angular.js' are excluded.

**File Preview** *(Sublime Text 3 Only)*

As you type, the current file and definition can be seen in the buffer giving to a quick view of the file as you search. If you wish to disable this feature, set `show_file_preview` to false in your User Settings.

Goto Definition Options
---
You can adjust the regex value of `non_word_chars` to change what type of chars should be considered word separators. By default, it's essentially Sublime Text's default word_separators sans the '-'.

Extending The Attribute List
---

You can extend this plug-in with your own custom attributes that you've created by
adding them to the `extended_attribute_list` property in the User Settings.

`add_indexed_directives` gives you a bare-bones completion of any directives that are added to the project index. This is enabled by default, but, you can turn this feature off by settings this property to `false`.

**Example** *add within 'Settings - User'*

```json
{
	"extended_attribute_list":[
		["my-directive\tMy Directives", "my-directive=\"${1:string}\"$0"],
	]
}
```

You can also override the `core_attribute_list` by setting that property within the User Settings.


Extending With Custom Components
---

You can also define custom components that you've created in AngularJS by adding them to the `angular_components`. By default, there are no components added to the list.

You can add some like so:

```json
{
	"angular_components":[
		"componentone",
		"componenttwo"
	]
}
```

Now you can have auto-complete on your custom elements.

Extending And Excluding Scopes
---

**Defining Tag Scopes**

By default, this plugin will only allow attribute completions within the scope of an HTML tag or within a [Jade](https://github.com/davidrios/jade-tmbundle) attribute list.

This can be changed by updating the property `attribute_defined_scopes`.

`attribute_defined_scopes` is just an array of scopes to determine whether or not the attribute auto-completion should react. Below is the default settings for this property.

```json
{
	"attribute_defined_scopes": [
		"text.html meta.tag - text.html punctuation.definition.tag.begin",
		"constant.name.attribute.tag.jade"
	]
}
```

**Excluding Scopes Within Tags**

Since scopes in Sublime Text cascade down, like CSS classes, you may find yourself in a situation where the attribute scope matches but you're within an inner scope, such as quotes, so the auto-completion is still triggered.

To prevent this occurence, you can define scopes to be excluded within the `attribute_avoided_scopes` property, quote scopes are excluded by default.

```json
{
	"attribute_avoided_scopes": [
		"string.quoted.double.html"
	]
}
```

Check out [this link](https://sublime-text-unofficial-documentation.readthedocs.org/en/latest/extensibility/syntaxdefs.html#scopes) for more information on scopes in Sublime Text.

**Defining Component Scopes**

This plugin will only allow component completions within the source scope of HTML or [Jade](https://github.com/davidrios/jade-tmbundle). Just like the attribute scope, this scope can be redefined as well. All you have to do is override the `component_defined_scopes` property which is also just an array of scopes. Below is the default setting for this property.

```json
{
	"component_defined_scopes": [
		"text.html - source",
		"source.jade"
	]
}
```

Strict Attribute Scope Matching
---

You can adjust the property `ensure_all_scopes_are_matched` to do strict matching on scopes (default is *false*). This means all scopes that are defined must be matched; otherwise, the attribute list will not appear.

In order for this option to be beneficial, you must define your own attribute scopes to strictly match.


AngularUI Attributes
---

This plugin is also shipped with completions for [AngularUI](http://angular-ui.github.io/). By default, these completions are disabled. To enable them update the `enable_AngularUI_directives` to `true` within the User Settings.

Data- Prefix
---

If your style is to add the `data-` prefix, you can enable this by setting the `enable_data_prefix` property to `true`.
