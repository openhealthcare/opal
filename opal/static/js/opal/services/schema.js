angular.module('opal.services').factory('Schema', function() {
    return function(columns) {
	    this.columns = columns;

	    this.getNumberOfColumns = function() {
	        return columns.length;
	    };

	    this.getColumn = function(columnName) {
            var result = _.find(columns, function(c){
                return c.name === columnName
            })

            if(result){
                return result;
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

        this.getAdvancedSearchColumns = function(){
            return _.filter(this.columns, function(c){
                return c.advanced_searchable
            })
        }
    };
});
