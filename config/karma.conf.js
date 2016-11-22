module.exports = function(config){
    var karmaDefaults = require('./karma_defaults.js');
    var karmaDir = __dirname;
    var staticRoute = "../../opal/opal/static/js";
    var coverageFiles = [
      'opal/**/*.js',
      '../../core/search/static/js/search/**/*.js',
    ];
    var files = [
      'opal/app.js',
      'opal/routes.js',
      '../../core/search/static/js/search/controllers/*',
      '../../core/search/static/js/search/services/*',
      'opaltest/*.js',
    ];

    var defaultConfig = karmaDefaults(karmaDir, staticRoute, coverageFiles, includedFiles);
    console.error(defaultConfig);
    config.set(defaultConfig);
}
