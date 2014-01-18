AngularJS Sublime Text Package
===

Installation Options
---
* [Package Control](http://wbond.net/sublime_packages/package_control)
* [Download](https://github.com/angular-ui/AngularJS-sublime-package/archive/master.zip) this repo, rename it to 'AngularJS', and place it within your `Packages` folder. This can be found within Sublime Text at `Preferences > Browse Packages…`
* Clone the repo into your `Packages` folder ` git clone git://github.com/angular-ui/AngularJS-sublime-package.git AngularJS`

Recommended Settings
---
Update your User Settings to the following. This setting update will automatically open the completion list for HTML attributes. You can add scopes for other preprocessor to get the list to automatically show.

(this is currently a ST3 default)

```js
// Controls what scopes auto complete will be triggered in)
"auto_complete_selector": "source - comment, meta.tag - punctuation.definition.tag.begin"
```

(this is currently a ST3 default)

```js
// For haml you could add
"auto_complete_selector": "source - comment, meta.tag - punctuation.definition.tag.begin, text.haml"
```

```js
// add for auto triggering controller completions within the ng-controller=""
"auto_complete_triggers":
	[
		{
			"characters": "ng-controller=\"*",
			"selector": "punctuation.definition.string"
		}
	]
```

Keymaps/Command Palette
---
`super+ctrl+l` : If not indexed: Indexes current project; If indexed: Opens quick panel with a list of definitions to search through

`super+ctrl+alt+l`: Attempts to goto definition (project must be indexed first)

`super+shift+ctrl+l`: Attempts to open browser to directive documentation at current cursor location


Plug-in Details
---

**Syntax File**

Provides a syntax file, HTML (Angular.js), that you can set to your view which adds the HTML scope back to `<script type="text/ng-template">` tags.

![
](http://angular-ui.github.io/AngularJS-sublime-package/images/screenshot-html-syntax-for-templates.png)

**Completions**

Provides auto-completion of core AngularJS directives, such as `ng-repeat`, `ng-click`, as well as any custom directives you create.

![
](http://angular-ui.github.io/AngularJS-sublime-package/images/screenshot-directives-auto-complete.png)


*The following completions require you to index your project*
--

(Index your project via `super+ctrl+l`)

Provides auto-completions for any directive as an HTML element, prefixed with `ngDir` to easily find via fuzzy search.

![
](http://angular-ui.github.io/AngularJS-sublime-package/images/screenshot-directive-element-completion.png)


Provides `isolate` scope completions (with binding types hinted on the right) specific to any directive used as an element, prefixed with `isolate` to easily find via fuzzy search.

![
](http://angular-ui.github.io/AngularJS-sublime-package/images/screenshot-isolate-scope-attribute-completions.png)


You can also get completions for filters within HTML markup. Trigger the completions list via `ctrl+space` right after typing `|  ` (pipe plus a space) and you should find all your filters that have been indexed within the completion list.

![](http://angular-ui.github.io/AngularJS-sublime-package/images/screenshot-filters-auto-complete.png)

Provides `controller` completions when the cursor is within the double quotes of `ng-controller=""`. You can have this triggered automatically via the settings provided in the 'Recommending Settings' section

![](http://angular-ui.github.io/AngularJS-sublime-package/images/screenshot-controller-auto-complete.png)

**Goto Definition**

Once you have your project indexed you can use the keyboard shortcut `super+alt+ctrl+l` when your cursor is within directive/services/etc.. and you'll be transported to the file that contains the definition.

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

#### Javascript Completions
* angular.copy
* angular.element
* angular.equals
* angular.extend
* angular.forEach
* angular.is[Array|Object|Defined|Function|String]
* angular.lowercase
* angular.noop
* angular.toJson
* angular.uppercase
* $apply
* $broadcast
* $destroy
* $digest
* $emit
* $eval
* $evalAsync
* $filter
* $http
* $log.log
* $new
* $on
* $parent
* $root
* $routeProvider.when
* $routeProvider.otherwise
* $watch
* directive
* module // Includes a preceeding docblock

___

Completion Options
---

Preferences > Package Settings > AngularJS > **Completions - User**

You can use the following properties to either extend or override the default completions provided.

**extended_attribute_list**: []; Allows you to extend the plug-in with more attributes

**angular_elements**: [*]; Default list of directives that can be used as HTML elements

**filter_list**: [*]; Default list of filters

**core_attribute_list**: [*]; Default list of filters

**AngularUI_attribute_list**: [*]; Default list of AngularUI directives

[*] - Adding any of these properties to your User file will override all default values for that setting

**Example** *Completions - User*

```json
{
	"extended_attribute_list":[
		["my-directive\tMy Directives", "my-directive=\"${1:string}\"$0"],
	]
}
```

Checkout the default completions settings (*Preferences > Package Settings > AngularJS > Completions - Default*) to see more examples.

___

Completion Settings
---

Preferences > Package Settings > AngularJS > **Settings - User**


**disable_all_completions**: false,

**disable_indexed_directive_completions**: false; *bare-bones completion of any directives that have been index*

**disable_indexed_isolate_completions**: false; *attempts to provide isolate scope completions when a directive is used as an element*

**disable_default_directive_completions**: false;

**disable_default_element_completions**: false;

**disable_default_js_completions**: false;

**enable_data_prefix**: bool (false); *adds the 'data-' prefix to attribute completions, note that you must still type 'ng-' to get autocompletion-list*

Example *Settings - User*, enable "data-" prefix

```json
{
	"enable_data_prefix": true
}
```

___

Indexing Options
---

Preferences > Package Settings > AngularJS > **Settings - User** *(requires project to be re-indexed)*

**match_definitions**: ["controller", "directive", "module", "factory", "filter"]; Determines what type of definitions to index

**excluded_dirs**: ["node_modules/"]; Global setting for excluding folders

**exclude_file_suffixes**: ["min.js", "angular.js"]; exclude files via their suffix

**Excluding Folders Per Project**

You can exclude folders at the project level by opening your project settings file `Project > Edit Project`

Example:

```json
"settings":
    {
        "AngularJS":
        {
            "exclude_dirs": ["someFolder/*/lib/angular/*"]
        }
    }
```

**Including Folders Per Project**

You can override the default project folders by setting the AngularJS `folders` variable within your projects settings `Project > Edit Project`

Example:

```json
{
	"folders":
	[
		{
			"follow_symlinks": true,
			"path": "/Users/username/Projects/example"
		}
	],
	"settings": {
		"AngularJS": {
			"folders": [
				"/Users/username/Projects/example/ng/src",
				"/Users/username/Vendors/someother/lib/outside/of/project"
			]
		}
	}
}
```

You can use 'shell-like' wildcards within your folder paths, they're expanded via the [glob](http://docs.python.org/2/library/glob.html#glob.glob) module.

___

Quick Panel Options
---

Preferences > Package Settings > AngularJS > **Settings - User** *(Sublime Text 3 Only)*

**show_file_preview**: bool(true); As you type, the current file and definition will be shown in the buffer

Example *Settings - User*, hide file preview

```json
{
	"show_file_preview": false
}
```
