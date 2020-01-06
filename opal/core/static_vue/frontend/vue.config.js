const { execSync } = require('child_process');
const BundleTracker = require("webpack-bundle-tracker");


/*
* Returns all the static directories of all the plugins
*/
var getPluginConfigs = function(){
  return JSON.parse(execSync('python ../manage.py static_asset_paths').toString());
}

const serving = process.env.SERVING === '1';
const publicPath = serving ? 'http://0.0.0.0:8080/' : '/assets/'

module.exports = {
    publicPath: publicPath,
    outputDir: './dist/',
    chainWebpack: config => {
        config.optimization
            .splitChunks(false)
        config
            .plugin('BundleTracker')
            .use(BundleTracker, [{filename: './webpack-stats.json'}])

        let entry = config.entry('app');
        let entries = getPluginConfigs();

        entries.forEach(entryPoint => {
          entry.add(entryPoint);
        });

        entry.add('./src/main.js')

        entry.end()

        config.devServer
            .public('http://0.0.0.0:8080')
            .host('0.0.0.0')
            .port(8080)
            .hotOnly(true)
            .watchOptions({poll: 1000})
            .https(false)
            .headers({"Access-Control-Allow-Origin": ["\*"]})
            }
        };
