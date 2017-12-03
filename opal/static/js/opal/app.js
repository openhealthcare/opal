!(function(){
  var app = OPAL.module('opal', [
      'ngRoute',
      'ngProgressLite',
      'opal.config',
    	'opal.filters',
    	'opal.services',
    	'opal.directives',
    	'opal.controllers',
      'ui.bootstrap',
      'ui.select'
  ]);
  OPAL.run(app);
})();
