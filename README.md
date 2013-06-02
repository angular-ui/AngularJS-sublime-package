AngularJS Sublime Text Package (Beta)
===

**Supports Sublime Text 2 and Sublime Text 3**

This plugin is a work in progress but should be functional for usage. The main development platform is OSX with the latest builds of Sublime Text 3. 

Checks are made in Sublime Text 2 when adding/modifying features so things should work correctly for ST2.

Installation Options
---
* [Download](https://github.com/angular-ui/AngularJS-sublime-package/archive/master.zip) this repo and place it within your `Packages` folder. This can be found within Sublime Text at `Preferences > Browse Packages…`

* Clone the repo into your `Packages` folder ` git clone git://github.com/angular-ui/AngularJS-sublime-package.git`

ST2 Recommended Settings
---
Update your User Settings to the following (this is a ST3 default)

```js
// Controls what scopes auto complete will be triggered in
"auto_complete_selector": "source - comment, meta.tag - punctuation.definition.tag.begin"
```

Keymaps/Command Palette
---
`super+ctrl+l` : If not indexed: Indexes current project; If indexed: Opens quick panel with a list of definitions to search through

`super+ctrl+alt+l`: Attempts to goto definition (project must be indexed first)

`super+shift+ctrl+l`: Attempts to open browser to directive documentation at current cursor location


Plug-in Details
---

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

**Excluding Folders Globally** *(requires project to be re-indexed)

You can exclude folders by adding them to the `exclude_dirs` property in the User Settings. By default 'node_modules/' is excluded, but you will need to add it back if you update the excluded_dirs property in your User Settings.

**Excluding Folders Per Project** *(requires project to be re-indexed)

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

You can use 'shell-like' wildcards within your folder paths, they're expanded via the [glob](http://docs.python.org/2/library/glob.html#glob.glob) module.

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


Extending/Altering Provided AngularJS Element Completions
---

You can add to or adjust the core AngularJS elements via the following user setting

```json
{
	"angular_elements":[]
}
```

AngularUI Attributes
---

This plugin is also shipped with completions for [AngularUI](http://angular-ui.github.io/). By default, these completions are disabled. To enable them update the `enable_AngularUI_directives` to `true` within the User Settings.

Data- Prefix
---

If your style is to add the `data-` prefix, you can enable this by setting the `enable_data_prefix` property to `true`.
