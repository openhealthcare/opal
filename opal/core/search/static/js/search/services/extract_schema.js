angular.module('opal.services').factory('ExtractSchema', function() {
    return function(columns) {
        this.columns = columns;

        this.getAdvancedSearchColumns = function(){
            return _.filter(this.columns, function(c){
                return c.advanced_searchable
            })
        }
    };
});
