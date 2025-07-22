const path = require("path");

module.exports = {
	entry: "./js/CSTest.js",   output: {
    		path: path.resolve(__dirname, "dist"),
    		filename: "bundle.js",     
    		libraryTarget: "umd",
  	},
	devtool: false,
	mode: "development",
  	resolve: { extensions: [".js"] },
};
