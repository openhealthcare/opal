describe('OPAL Directives', function(){

    var element, scope;

    beforeEach(module('opal'));
    beforeEach(module('opal.directives'));

    beforeEach(inject(function($rootScope, $compile) {
        scope = $rootScope.$new();
    }));

    function compileDirective(tpl){
        // inject allows you to use AngularJS dependency injection
        // to retrieve and use other services
        inject(function($compile) {
            element = $compile(tpl)(scope);
        });
        // $digest is necessary to finalize the directive generation
        scope.$digest();
    }

    describe('fixHeight', function(){
        it('shoud set the heigh', function(){
            var markup = '<div class="patient-list-container" fix-height></div>';
            compileDirective(markup);
            scope.$destroy();
            expect(element.attr('style').indexOf('height: ')).toEqual(0);
        });
    });

    describe('scrollEpisodes', function(){

        it('should check on down', function(){
            scope.isSelectedEpisode = true
            spyOn(scope, 'isSelectedEpisode').and.returnValue(true);

            var markup = '<div class="patient-list-container">'+
                '<div scroll-episodes="isSelectedEpisode" scroll-container=".patient-list-container"></div>' +
                '<table><thead height="200"></thead></table></div>';

            compileDirective(markup);

            spyOn(element[0], 'getBoundingClientRect').and.returnValue({top:0, bottom:-2})

            scope.$broadcast('keydown',{ keyCode: 38});
            expect(scope.isSelectedEpisode).toHaveBeenCalled();
        });

        it('should check on down', function(){
            scope.isSelectedEpisode = true
            spyOn(scope, 'isSelectedEpisode').and.returnValue(true);
            var markup = '<div scroll-episodes="isSelectedEpisode"></div>';
            compileDirective(markup);
            scope.$broadcast('keydown',{ keyCode: 40});
            expect(scope.isSelectedEpisode).toHaveBeenCalled();
        });

    });

    describe('markdown', function(){
        it('should be markdowny', function(){
            var markup = '<div markdown="foo"></div>';
            scope.editing = {foo: 'bar'}
            compileDirective(markup);
        });
    })

    describe('blurOthers', function(){
        it('should be blurred', function(){
            var markup = '<div blur-others></div>';
            compileDirective(markup);
        })
    })

});
