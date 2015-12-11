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
            var pageStart;

            /*
            * assuming a page size of 10
            * when we've got 11 results we want 2 pages
            * when we've got 101 results and we're on page 4
            * we want to see "previous 4, 5, 6, 7, 8, 9 next"
            * when we're on page 11 we want to see previous 6, 7, 8, 9, 10, 11
            */

            if(this.pageNumber < numberOfPageResultsDisplayed){
                pageStart = 1;
            }
            else{
                pageStart = Math.min(args.total_pages - numberOfPageResultsDisplayed, this.pageNumber);
            }

            var pageEnd = Math.min(pageStart + numberOfPageResultsDisplayed, args.total_pages);
            this.totalPages = _.range(pageStart, pageEnd + 1);
            this.hasNext = args.total_pages > numberOfPageResultsDisplayed + this.pageNumber;
            this.hasPrevious = pageStart !== 1;
        }
        else{
            this.pageNumber = 1;
        }
    };

    return Paginator;
});
