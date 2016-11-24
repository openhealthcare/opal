module.exports = function(config){
    var karmaDefaults = require('./karma_defaults.js');
    var baseDir = __dirname + "/..";
    var coverageFiles = [
      'opal/**/*.js',
      '../../core/search/static/js/search/**/*.js',
    ];
    var includedFiles = [
      'opal/app.js',
      'opal/routes.js',
      '../../core/search/static/js/search/controllers/*',
      '../../core/search/static/js/search/services/*',
      'opaltest/*.js',
    ];

    var defaultConfig = karmaDefaults(includedFiles, baseDir, coverageFiles);
    config.set(defaultConfig);
}
