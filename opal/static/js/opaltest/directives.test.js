describe('OPAL Directives', function(){

    var element, scope, $timeout, $httpBackend;
    var responseMarkUp = ' \
      <ui-select class="col-sm-8" multiple ng-model="value" on-remove="onRemove($item, $model)" on-select="onSelect($item, $model)" theme="bootstrap"> \
        <ui-select-match>[[ $item.display_name ]]</ui-select-match> \
        <ui-select-choices repeat="i.name as i in tagsList | filter:$select.search" value="[[ $select.selected.name ]]"> \
          <div ng-bind-html="i.display_name | highlight: $select.search"></div>  \
        </ui-select-choices> \
      </ui-select> \
    ';

    var metaData = {tags: {
      id_inpatients: {
        direct_add: true,
        display_name: "ID Inpatients",
        name: "id_inpatients",
        parent_tag: "infectious_diseases",
        slug: "infectious_diseases-id_inpatients"
      },
      infectious_diseases: {
        direct_add: false,
        display_name: "Infectious Diseases",
        name: "infectious_diseases",
        }
      }
    }
    beforeEach(module('opal'));


    beforeEach(module('ui.select'));

    beforeEach(module('opal.directives', function($provide){
      $provide.service('Metadata', function(){
        return {
          then: function(fn){
            fn(metaData);
          }
        };
      });
    }));

    beforeEach(function(){
      var $rootScope;

      inject(function($injector){
        $timeout = $injector.get('$timeout');
        $rootScope = $injector.get('$rootScope');
        $templateCache = $injector.get('$templateCache');
      });

      $templateCache.put('/templates/ng_templates/tag_select.html', responseMarkUp);
      scope = $rootScope.$new();
    });

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

        it('should animate on click', function() {
            var markup = '<button scroll-top></button>';
            spyOn($.fn, "animate");
            compileDirective(markup);
            $(element).click();
            expect($.fn.animate).toHaveBeenCalledWith({ scrollTop: '0' });
        });
    })

    describe('goToTop', function(){
      it('should compile', function() {
          var markup = '<button go-to-top>hello</button>';
          spyOn($.fn, "scrollTop");
          compileDirective(markup);
          $(element).click();
          expect($.fn.scrollTop).toHaveBeenCalledWith(0);
      });
    });

    describe('placeholder', function() {

        it('should display the', function() {
            spyOn($, "support");
            $.support.placeholder = true;
            var markup = '<input placeholder="foo" />';
            compileDirective(markup);
            expect(_.contains(element[0], 'placeholder="foo"'));
        });

        it('should display the', function() {
            spyOn($, "support");
            $.support.placeholder = false;
            var markup = '<input placeholder="foo" />';
            compileDirective(markup);
            expect(_.contains(element[0], 'placeholder="foo"'));
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

    describe('oneClickOnly', function(){
        it('should disable buttons on click and call through', function(){
            var clickfn = jasmine.createSpy('clickfn');
            scope.clickfn = clickfn;
            var markup = '<button one-click-only ng-click="clickfn()">Save</button>'
            compileDirective(markup);
            $(element).click();
            expect(clickfn.calls.count()).toEqual(1);
            expect($(element).prop('disabled')).toBe(true);
        });

        it('should not disable clicks if a variable is set', function(){
            // if a form is invalid, we don't want to disable clicks
            var clickfn = jasmine.createSpy('clickfn');
            scope.clickfn = clickfn;
            scope.oneClick = true;
            var markup = '<button one-click-only="oneClick" ng-click="clickfn()">Save</button>'
            compileDirective(markup);
            scope.oneClick = false;
            $(element).click();
            expect(clickfn.calls.count()).toEqual(1);
            expect($(element).prop('disabled')).toBe(false);
        });
    });

    describe('clipboard', function(){
        var markup = '<button class="btn btn-primary" clipboard data-clipboard-target="#content">copy</button>'
        var growlSuccessSpy, growlErrorSpy, clipboardSpy;
        var successFn;
        var errorFn;
        var growl;

        beforeEach(inject(function(_growl_) {
            growl = _growl_;
            spyOn(growl, "error");
            spyOn(growl, "success");
        }));


        beforeEach(function(){
            clipboardSpy = jasmine.createSpy('clipboard');
            clipboardSpy.and.callFake(function(x, y){

                if(x === "success"){
                    successFn = y
                }
                else if(x === "error"){
                    errorFn = y
                }
                else{
                  fail();
                }
            });
            spyOn(window, "Clipboard").and.returnValue({on: clipboardSpy});
            compileDirective(markup);
        })

        it('should display the growl success message on success', function(){
          successFn();
          scope.$digest();
          expect(growl.success).toHaveBeenCalledWith('Copied');
        });

        it('should display the growl error message on fail', function(){
          errorFn("can't");
          expect(growl.error).toHaveBeenCalledWith("Failed to copy can't");
        });

        it('should not display the growl error message if the directive is told not to', function(){
          var markup = '<button class="btn btn-primary" clipboard clipboard-show-growl="false" data-clipboard-target="#content">copy</button>'
          compileDirective(markup);
          successFn();
          errorFn();
          expect(growl.success.calls.any()).toBe(false);
        });

        it('should call the success function if provided', function(){
            scope.called = function(){}
            spyOn(scope, "called");
            var markup = '<button class="btn btn-primary" clipboard clipboard-success="called()" data-clipboard-target="#content">copy</button>'
            compileDirective(markup);
            successFn();
            expect(scope.called).toHaveBeenCalled();
        });

        it('should call the error function if provided', function(){
            scope.called = function(){}
            spyOn(scope, "called");
            var markup = '<button class="btn btn-primary" clipboard clipboard-error="called()" data-clipboard-target="#content">copy</button>'
            compileDirective(markup);
            errorFn();
            expect(scope.called).toHaveBeenCalled();
        });
    });

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

    describe("tag-select", function(){
      var markup = '<form name="form"><div id="test" tag-select ng-model="editing.tagging"></div></form>';

      it("should render a template", function(){
        scope.editing = {tagging: {}};
        compileDirective(markup);
        var input = angular.element($(element).find(".ui-select-container")[0]);
        var testScope = input.scope();
        expect(testScope.value).toEqual([]);
      });

      it("should copy values through to the select 2", function(){
        scope.editing = {tagging: {id_inpatients: true}};
        compileDirective(markup);
        var input = angular.element($(element).find(".ui-select-container")[0]);
        var testScope = input.scope();
        expect(testScope.value.length).toBe(1)
        expect(testScope.value[0].display_name).toBe("ID Inpatients");
      });

      it("should update editing if something is added", function(){
        scope.editing = {tagging: {}};
        compileDirective(markup);
        var input = angular.element($(element).find(".ui-select-container")[0]);
        var testScope = input.scope();
        testScope.onSelect(metaData.tags.id_inpatients, "id_inpatients");
        expect(scope.editing.tagging.id_inpatients).toBe(true);
      });

      it("should update editing if something is removed", function(){
        scope.editing = {tagging: {id_inpatients: true}};
        compileDirective(markup);
        var input = angular.element($(element).find(".ui-select-container")[0]);
        var testScope = input.scope();
        testScope.onRemove(metaData.tags.id_inpatients, "id_inpatients");
        expect(scope.editing.tagging.id_inpatients).toBe(false);
      });

      it("should not remove from if its not in tags", function(){
        scope.editing = {tagging: {id_inpatients: true, microHaem: true}};
        compileDirective(markup);
        var input = angular.element($(element).find(".ui-select-container")[0]);
        var testScope = input.scope();
        testScope.onRemove(metaData.tags.id_inpatients, "id_inpatients");
        expect(scope.editing.tagging.microHaem).toBe(true);
      });

      it("should not remove from if its a parent tag", function(){
        scope.editing = {tagging: {id_inpatients: true, infectious_diseases: true}};
        compileDirective(markup);
        var input = angular.element($(element).find(".ui-select-container")[0]);
        var testScope = input.scope();
        testScope.onRemove(metaData.tags.id_inpatients, "id_inpatients");
        expect(scope.editing.tagging.infectious_diseases).toBe(true);
      });
    });
});
