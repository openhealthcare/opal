var app = OPAL.module('opal', [
    'ngRoute',
    'ngProgressLite',
	'opal.filters',
	'opal.services',
	'opal.directives',
	'opal.controllers',
    'ui.bootstrap',
]);
OPAL.run(app);
