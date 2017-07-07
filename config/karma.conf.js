module.exports = function(config){
    var opalPath = process.env.OPAL_LOCATION;
    var karmaDefaults = require(opalPath + '/opal/tests/js_config/karma_defaults.js');
    var baseDir = __dirname + "/..";
    var coverageFiles = [
      'opal/**/*.js',
      '../../core/search/static/js/search/**/*.js',
      '../../core/pathway/static/js/pathway/**/*.js',
    ];
    var includedFiles = [
      'opal/app.js',
      'opal/routes.js',
      '../../core/search/static/js/search/controllers/*',
      '../../core/search/static/js/search/services/*',
      'test/*.js',
      '../../core/search/static/js/test/*',
      '../../core/pathway/static/js/test/*',
    ];

    var defaultConfig = karmaDefaults(includedFiles, baseDir, coverageFiles);
    config.set(defaultConfig);
}
