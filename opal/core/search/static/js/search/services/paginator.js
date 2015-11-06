angular.module('opal.services').factory('Paginator', function() {
    var numberOfPageResultsDisplayed = 6;

    // paginator expects a function to be called when
    // you click on the next or the previous and it's
    // passed the page number -1/+1 of the currentPageNumber
    // paginator expects an args object
    // "page_number", "total_pages"
    // it also expects you to set functions on
    // onGoNext and onGoPrevious, these will
    // be called with the current page number
    var Paginator = function(goOn, args){
        this.goPrevious = function(){
            goOn(this.pageNumber - 1);
        }

        this.goNext = function(){
            goOn(this.pageNumber + 1);
        }

        if(args){
            this.pageNumber = args.page_number;
            this.totalCount = args.total_count;
            this.hasPrevious = pageStart !== 1;
            var pageStart = Math.min(args.total_pages - numberOfPageResultsDisplayed, this.pageNumber);
            pageStart = Math.max(pageStart, 1);
            var pageEnd = Math.min(pageStart + numberOfPageResultsDisplayed, args.total_pages);
            this.totalPages = _.range(pageStart, pageEnd);
            this.hasNext = args.total_pages > numberOfPageResultsDisplayed;
            this.hasPrevious = pageStart !== 1;
        }
        else{
            this.pageNumber = 1;
        }
    };

    return Paginator;
});
