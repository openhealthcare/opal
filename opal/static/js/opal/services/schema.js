angular.module('opal.services').factory('Schema', function() {
    return function(columns) {
	    this.columns = columns;

	    this.getNumberOfColumns = function() {
	        return columns.length;
	    };

	    this.getColumn = function(columnName) {
	        var column;
	        for (cix = 0; cix < this.getNumberOfColumns(); cix++) {
		        column = columns[cix];
		        if (column.name == columnName) {
		            return column;
		        }
	        }
	        throw 'No such column with name: "' + columnName + '"';
	    };

	    this.isSingleton = function(columnName) {
	        var column = this.getColumn(columnName);
	        return column.single;
	    };

        this.isReadOnly = function(columnName) {
            var column = this.getColumn(columnName);
            return column.readOnly;
        }
    };
});
