describe('OPAL Directives', function(){
    "use strict";

    var $templateCache, $timeout, $httpBackend, $rootScope, $compile;
    var element, scope, $exceptionHandler;
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
        id_liason: {
            direct_add: true,
            display_name: "ID Liason",
            name: "id_liason",
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
                load: function(){
                  return {
                    then: function(fn){
                        fn(metaData);
                    }
                  };
                }
            };
        });
    }));

    beforeEach(function(){

        inject(function($injector){
            $timeout          = $injector.get('$timeout');
            $rootScope        = $injector.get('$rootScope');
            $templateCache    = $injector.get('$templateCache');
            $exceptionHandler = $injector.get('$exceptionHandler');
            $httpBackend      = $injector.get('$httpBackend');
            $compile = $injector.get('$compile');
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

    describe('setFocusIf', function(){
        it('should set focus if true', function(){
          var markup = '<input type="text" set-focus-if="true" />';
          compileDirective(markup);
          spyOn(element[0],'focus');
          $timeout.flush();
          expect(element[0].focus).toHaveBeenCalled();
        });

        it('should not set focus if false', function(){
          var markup = '<input type="text" set-focus-if="false" />';
          compileDirective(markup);
          spyOn(element[0],'focus');
          $timeout.verifyNoPendingTasks();
        });

        it('should set focus on change to positive', function(){
          scope.something = true;
          var markup = '<input type="text" set-focus-if="!something" />';
          compileDirective(markup);
          spyOn(element[0],'focus');

          $timeout.verifyNoPendingTasks();
          scope.something = false;
          scope.$apply();
          $timeout.flush();
          expect(element[0].focus).toHaveBeenCalled();
        });

        it('should not set focus on change to negative', function(){
          scope.something = false;
          var markup = '<input type="text" set-focus-if="!something" />';
          compileDirective(markup);
          spyOn(element[0],'focus');

          $timeout.flush();
          expect(element[0].focus).toHaveBeenCalled();

          scope.something = true;
          scope.$apply();

          $timeout.verifyNoPendingTasks();
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
            spyOn(scope, 'isScrolledIntoView').and.returnValue(false);

            spyOn(element[0], 'getBoundingClientRect').and.returnValue({top:0, bottom:-2})

            scope.$broadcast('keydown',{ keyCode: 38});
            expect(scope.isSelectedEpisode).toHaveBeenCalled();
        });

        it('should check on down', function(){
            scope.isSelectedEpisode = true
            spyOn(scope, 'isSelectedEpisode').and.returnValue(true);
            var markup = '<div scroll-episodes="isSelectedEpisode"></div>';
            compileDirective(markup);
            spyOn(scope, 'isScrolledIntoView').and.returnValue(false);

            scope.$broadcast('keydown',{ keyCode: 40});
            expect(scope.isSelectedEpisode).toHaveBeenCalled();
        });

        it('should not scroll if we are in view', function(){
            scope.isSelectedEpisode = true
            spyOn(scope, 'isSelectedEpisode').and.returnValue(true);
            var markup = '<div scroll-episodes="isSelectedEpisode"></div>';
            compileDirective(markup);

            scope.$broadcast('keydown',{ keyCode: 40});
            expect(scope.isSelectedEpisode).toHaveBeenCalled();
        });

    });

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

        it('should still have a placeholder if we supprt them', function() {
            $.support.placeholder = true;
            var markup = '<input placeholder="foo" />';
            compileDirective(markup);
            expect(_.contains(element[0], 'placeholder="foo"'));
        });

        it('should set the value', function() {
            spyOn($, "support");
            $.support.placeholder = false;
            var markup = '<input placeholder="foo" />';
            compileDirective(markup);
            $timeout.flush();
            expect($(element).val()).toEqual('foo')
        });

        it('focus() should nuke the value', function() {
            spyOn($, "support");
            $.support.placeholder = false;
            var markup = '<input placeholder="foo" />';
            compileDirective(markup);
            $timeout.flush();
            $(element[0]).triggerHandler('focus')
            expect($(element).val()).toEqual('')
        });

        it('focus() then blur() should keep the value', function() {
            spyOn($, "support");
            $.support.placeholder = false;
            var markup = '<input placeholder="foo" />';
            compileDirective(markup);
            $timeout.flush();
            $(element[0]).triggerHandler('focus')
            $(element[0]).triggerHandler('blur')
            expect($(element).val()).toEqual('foo')
        });

        it('should return if a password', function() {
            spyOn($, "support");
            $.support.placeholder = false;
            var markup = '<input type="password" placeholder="foo" />';
            compileDirective(markup);
            expect(_.contains(element[0], 'placeholder="foo"'));
        });

        it

    });

    describe('parentHeight', function(){

        it('should be markdowny', function(){
            var markup = '<div style="height: 200px"><div markdown="foo"></div></div>';
            scope.editing = {foo: 'bar'}
            compileDirective(markup);
            expect($(element).height()).toBe(200);
        });

    });

    describe('markdown', function(){
        it('should render markdown', function(){
            var markup = '<div markdown># foo</div>';
            compileDirective(markup);
            expect($(element).html()).toEqual('<h1 id="foo">foo</h1>');
        });

        it('should be markdowny', function(){
            var markup = '<div markdown="foo"></div>';
            scope.editing = {foo: 'bar'}
            compileDirective(markup);
            expect($(element).html()).toEqual('<p>bar  </p>');
        });

        it("should do nothing if we can't find item or editing", function(){
            var markup = '<div markdown="foo"></div>';
            compileDirective(markup);
            expect($(element).html()).toEqual('');
        });

    })

    describe('slashkeyfocus', function() {

        it('should focus if we press /', function() {
            var markup = '<input slash-key-focus="!state || state===\'normal\'"/>';
            compileDirective(markup);
            expect($(element).is(":focus")).toEqual(false)
            spyOn(element[0], 'focus')
            var e = $.Event('keyup.keyFocus');
            e.keyCode = 191
            $(window).trigger(e)
            expect(element[0].focus).toHaveBeenCalled()
        });

        it('should blur if we ESC', function() {
            var markup = '<input slash-key-focus="!state || state===\'normal\'"/>';
            compileDirective(markup);
            document.body.appendChild(element[0]);
            var e = $.Event('keyup.keyBlur')
            e.keyCode = 27
            spyOn(element[0], 'blur').and.callThrough()
            $(element).focus().trigger(e)
            expect(element[0].blur).toHaveBeenCalled()
        });

        it('it should remove the on event if the slash-key-focus is removed', function(){
          var markup = '<input slash-key-focus="!state"/>';
          compileDirective(markup);
          expect($(element).is(":focus")).toEqual(false)
          spyOn(element[0], 'focus')
          scope.$apply();
          scope.state = true;
          scope.$apply();
          var e = $.Event('keyup.keyFocus');
          e.keyCode = 191
          $(window).trigger(e)
          expect(element[0].focus).not.toHaveBeenCalled();
        });
    });

    describe("freezeHeaders", function(){
        it('should apply the stick table headers jquery directive', function(){
            $.fn.stickyTableHeaders = function(){};
            spyOn($.fn, "stickyTableHeaders");
            var markup = '<div freeze-headers><table></tablre></div>';
            compileDirective(markup);
            expect($.fn.stickyTableHeaders).toHaveBeenCalled();
        });
    });

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

    describe('checkForm', function(){
        it('should disable the button if there are errors', function(){
            scope.editing = {something: ""};
            var clickfn = jasmine.createSpy('clickfn');
            scope.clickfn = clickfn;

            var markup = '<form name="form"><input required ng-model="editing.something" ng-click="clickfn()"><button check-form="form">Save</button></form>';
            compileDirective(markup);
            var btn = $(element.find("button"));
            btn.click();
            var innerscope = angular.element(btn).scope();
            expect(btn.prop('disabled')).toBe(true);
            expect(clickfn).not.toHaveBeenCalled();
            expect(innerscope.form.$submitted).toBe(true);
        });

        it('should undisable the button if all errors are fixed', function(){
            scope.editing = {something: ""};
            var markup = '<form name="form"><input required ng-model="editing.something"><button check-form="form">Save</button></form>';
            compileDirective(markup);
            var btn = $(element.find("button"));
            btn.click();
            var innerscope = angular.element(btn).scope();
            var input = $(element.find("input"));
            expect(btn.prop('disabled')).toBe(true);
            expect(innerscope.form.$submitted).toBe(true);
            scope.editing.something = 'hello';
            scope.$apply();
            expect(btn.prop('disabled')).toBe(false);
        });

        it('should change the button to disabled if the form has been submitted', function(){
            scope.editing = {something: ""};
            scope.clickfn = jasmine.createSpy('clickfn');
            var markup = '<form name="form"><input ng-model="editing.something"><button check-form="form" ng-click="clickfn()">Save</button></form>';
            compileDirective(markup);
            var btn = $(element.find("button"));
            btn.click();
            scope.$apply();
            var innerscope = angular.element(btn).scope();
            var input = $(element.find("input"));
            expect(innerscope.form.$valid).toBe(true);
            expect(btn.prop('disabled')).toBe(true);
            expect(scope.clickfn.calls.count()).toEqual(1);
        });

        it('should handle the issue for when the form var is removed on submission', function(){
            scope.editing = {something: ""};
            scope.clickfn = jasmine.createSpy('clickfn');
            var markup = '<form name="form"><input ng-model="editing.something"><button check-form="form" ng-click="clickfn()">Save</button></form>';
            compileDirective(markup);
            scope.$apply();
            var btn = $(element.find("button"));
            var innerscope = angular.element(btn).scope();
            expect(!!innerscope.form).toBe(true);
            innerscope.form = undefined;
            scope.$apply();
        });

        it('should handle the case when the form is submitted in an invalid state, these are then corrected, then made invalid, then corrected', function(){
            /*
             * we had the case that the validation button was stuck in an invalid
             * state if the user entered invalid options after the form was submitted
             * even after they were fixed, the button remained disabled
             */
            scope.editing = {something: ""};
            var markup = '<form name="form"><input required ng-model="editing.something"><button check-form="form">Save</button></form>';
            compileDirective(markup);
            var btn = $(element.find("button"));
            btn.click();
            var innerscope = angular.element(btn).scope();
            var input = $(element.find("input"));
            expect(btn.prop('disabled')).toBe(true);
            expect(innerscope.form.$submitted).toBe(true);
            scope.editing.something = 'hello';
            scope.$apply();
            expect(btn.prop('disabled')).toBe(false);
            scope.editing.something = "";
            scope.$apply();
            expect(btn.prop('disabled')).toBe(true);

            scope.editing.something = 'hello';
            scope.$apply();
            expect(btn.prop('disabled')).toBe(false);
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

    describe('dateOfBirth', function(){
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

        it('should throw if no model is set', function(){
          var markup = '<div id="test" date-of-birth name="date_of_birth"></div>';
          scope.editing = scopeBinding;
          expect(function(){ compileDirective(markup) }).toThrow(
            "date-of-birth requires an ng-model to be set"
          );
        })

        it('should have a placeholder which displays the desired date format', function(){
            expect($(input).attr("placeholder")).toEqual("DD/MM/YYYY");
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

        it("should mark as invalid if its not a valid date", function(){
            expect(testScope.numberCheck.test("12/14/2000")).toBe(false);
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

    describe("tagSelect", function(){
        var markup = '<form name="form"><div id="test" tag-select ng-model="editing.tagging"></div></form>';

        it("requires ng-model to be set", function(){
          var markup = '<div tag-select></div>';
          expect(function(){ compileDirective(markup) }).toThrow(
            "tag-select requires an ng-model to be set"
          );
        });


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

        it("should sort the copied values by alphabetical order", function(){
          scope.editing = {tagging: {
            id_inpatients: true,
            id_liason: true
          }};
          compileDirective(markup);
          var input = angular.element($(element).find(".ui-select-container")[0]);
          var testScope = input.scope();
          expect(testScope.value.length).toBe(2)
          expect(testScope.value[0].display_name).toBe("ID Inpatients");
          expect(testScope.value[1].display_name).toBe("ID Liason");
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

    describe('User details directives', function() {
        var userdata;

        beforeEach(function(){
            userdata = {
                full_name:'Jane Doe',
                avatar_url: 'http://localhost/avatar.gif'
            }
            $httpBackend.whenGET('/api/v0.1/user/1/').respond(userdata)
        })

        describe('fullNameForUser', function() {

            it('should set the contents to be the name of the user', function() {
                compileDirective('<span full-name-for-user="1"></span>');
                $httpBackend.flush();
                $rootScope.$apply();
                expect($(element).text()).toEqual('Jane Doe')
            });

        });

        describe('avatarForUser', function() {

            it('should set the src', function() {
                compileDirective('<img avatar-for-user="1" />');
                $httpBackend.flush();
                $rootScope.$apply();
                expect($(element).attr('src')).toEqual('http://localhost/avatar.gif');
            });

        });
    });

    describe('timeSet', function(){
      var markup = "<div time-set-change='someFun()' time-set='editing.subrecord.someField'><div>[[ internal.time_field ]]</div></div>";

      it("should add a new date to the scope if there isn't alread one", function(){
        var compiled = $compile(markup)(scope);
        var innerScope = angular.element($(compiled).find("div")[0]).scope();
        scope.$digest();
        var now = new Date();
        expect(_.isDate(innerScope.internal.time_field)).toBe(true);
        expect(innerScope.internal.time_field.getHours()).toBe(now.getHours());
        expect(innerScope.internal.time_field.getMinutes()).toBe(now.getMinutes());
      });

      it("should use the existing date if there is one", function(){
        scope.editing = {
          subrecord: {someField: "20:12:10"}
        }
        var compiled = $compile(markup)(scope);
        var innerScope = angular.element($(compiled).find("div")[0]).scope();
        scope.$digest();
        expect(_.isDate(innerScope.internal.time_field)).toBe(true);
        expect(innerScope.internal.time_field.getHours()).toBe(20);
        expect(innerScope.internal.time_field.getMinutes()).toBe(12);
      });

      it('should update the outside scope if the internal var is changed', function(){
        scope.editing = {
          subrecord: {someField: "20:12:10"}
        }
        var compiled = $compile(markup)(scope);
        var innerScope = angular.element($(compiled).find("div")[0]).scope();
        scope.$digest();
        innerScope.internal.time_field = new Date(2017, 12, 12, 10, 23)
        scope.$digest();
        expect(scope.editing.subrecord.someField).toBe("10:23:00");
      });

      it('should update the inside scope if the external var is changed', function(){
        scope.editing = {
          subrecord: {someField: "20:12:10"}
        }
        var compiled = $compile(markup)(scope);
        var innerScope = angular.element($(compiled).find("div")[0]).scope();
        scope.$digest();
        scope.editing.subrecord.someField = "21:50:10"
        scope.$digest();
        expect(_.isDate(innerScope.internal.time_field)).toBe(true);
        expect(innerScope.internal.time_field.getHours()).toBe(21);
        expect(innerScope.internal.time_field.getMinutes()).toBe(50);
      });
    });
});
