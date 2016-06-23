describe('OPAL Directives', function(){

    var element, scope, $timeout;

    beforeEach(module('opal.directives'));

    beforeEach(inject(function($rootScope, $compile) {
        scope = $rootScope.$new();
    }));

    beforeEach(inject(function(_$timeout_) {
        $timeout = _$timeout_;
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

    describe('autofocus', function(){
        it('should set autofocus', function(){
            var markup = '<input type="text" autofocus />';
            compileDirective(markup);
            spyOn(element[0],'focus');
            $timeout.flush();
            expect(element[0].focus).toHaveBeenCalled();
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

    describe('scrollTop', function(){

        it('should', function() {
            var markup = '<div scroll-top></div';
            compileDirective(markup);

        });

    })

    describe('placeholder', function() {

        it('should ', function() {
            var markup = '<input placeholder="foo" />';
            compileDirective(markup);
        });

    });

    describe('slashkeyfocus', function() {
      it('should do something', function() {
          var markup = '<input slash-key-focus />';
          compileDirective(markup);
      });
    });

    describe('markdown', function(){
        it('should be markdowny', function(){
            var markup = '<div markdown="foo"></div>';
            scope.editing = {foo: 'bar'}
            compileDirective(markup);
        });
    })

    describe('date-of-birth', function(){
        var scopeBinding = {date_of_birth: moment("10/12/1999", "DD/MM/YYYY", true)}
        var testScope;
        var input;
        var markup = '<form name="form"><div id="test" date-of-birth name="date_of_birth" ng-model="editing.date_of_birth"></div></form>'

        beforeEach(function(){
            scope.editing = scopeBinding;
            compileDirective(markup);
            input = angular.element($(element).find("input")[0]);
            testScope = input.scope();
        });

        it('should change change the core moment into a date string', function(){
            expect(testScope.value).toEqual("10/12/1999");
        });

        it('should handle the case where there is no date of birth', function(){
            scope.editing = {};
            compileDirective(markup);
            var input = angular.element($(element).find("input")[0]);
            var testScope = input.scope();
            expect(testScope.value).toBe(undefined);
        });

        it('it should reset the value when changed', function(){
            expect(testScope.value).toEqual("10/12/1999");
            scope.editing.date_of_birth = undefined;
            scope.$apply();
            expect(testScope.value).toBe(undefined);
        });

        it('should change inputs to moments', function(){
            testScope.value = "11/01/2000";
            testScope.onChange();
            expect(scopeBinding.date_of_birth.format("DD/MM/YYYY")).toEqual("11/01/2000");
        });

        it("should mark as invalid if its not a valid date string", function(){
            expect(testScope.numberCheck.test("wrongwrong")).toBe(false);
        });

        it("should mark as invalid if the date is over 150", function(){
            expect(testScope.numberCheck.test("10/1/1200")).toBe(false);
        });

        it("should mark as invalid if the date is in the future", function(){
            expect(testScope.numberCheck.test("10/1/4000")).toBe(false);
        });
        it("should mark as invalid if the year is too long", function(){
            expect(testScope.numberCheck.test("10/1/19994000")).toBe(false);
        });

        it("should not render a string as a moment if its a string", function(){
            /*
            * item changes dates to strings before passing them off
            * we don't want this change to show on the front end
            */
            scope.editing = {date_of_birth: "19/10/2001"};
            compileDirective(markup);
            var input = angular.element($(element).find("input")[0]);
            var testScope = input.scope();
            expect(testScope.value).toBe("19/10/2001");
        });
    });
});
