describe('Utils.OPAL._run', function (){
    "use strict";

    it('should reset ngProgressLite on route change error', function(){
      var mockScope = jasmine.createSpyObj(["$on"]);
      var ngProcessLite = jasmine.createSpyObj(['set']);
      var mock_modal = { open: function(){} };
      OPAL._run(mockScope, ngProcessLite, mock_modal);
      expect(mockScope.$on).toHaveBeenCalled();
      var runFun = mockScope.$on.calls.argsFor(2)[1];
      expect(mockScope.$on.calls.argsFor(2)[0]).toBe('$routeChangeError');
      runFun();
      expect(ngProcessLite.set).toHaveBeenCalledWith(0);
    });

    it('Should add open_modal to the root scope.', function () {
        var mock_scope = { $on: function(){} };
        var mock_modal = { open: function(){} };

        OPAL._run(mock_scope, {}, mock_modal)

        expect(mock_scope.open_modal).toBeDefined();
    });

    it('Should open a modal with the arguments', function () {
        var passedFunction;
        var mock_scope = { $on: function(){} };
        var mock_then = {
          result: {
            then: function(x){ passedFunction = x; }
          }
        };
        var mock_modal = { open: function(){ return mock_then } };
        spyOn(mock_modal, 'open').and.callThrough();
        spyOn(mock_then, 'result');

        OPAL._run(mock_scope, {}, mock_modal)
        var fake_modal = mock_scope.open_modal('TestCtrl', 'template.html', {episode: {}})

        var call_args = mock_modal.open.calls.mostRecent().args[0];

        expect(call_args.controller).toBe('TestCtrl');
        expect(call_args.templateUrl).toBe('template.html');
        expect(call_args.resolve.episode()).toEqual({});
        expect(mock_scope.state).toBe('modal');
        passedFunction();
        expect(mock_scope.state).toBe('normal');
    });

    it('Should add dateHelper to the root scope.', function () {
        var mock_scope = { $on: function(){} };
        OPAL._run(mock_scope, {}, {})
        expect(mock_scope.dateHelper).toBeDefined();
    });

    it('Should provide the current datetime when dateHelper.now() is called', function () {
        var mock_scope = { $on: function(){} };
        OPAL._run(mock_scope, {}, {});
        var now = moment(mock_scope.dateHelper.now());
        expect(now.isSame(moment(), 'minute')).toBe(true);
    });

    it('Should provide the yesterdays datetime when dateHelper.yesterday() is called', function () {
        var mock_scope = { $on: function(){} };
        OPAL._run(mock_scope, {}, {})
        var yesterday = moment().subtract(1, "day");
        expect(moment(mock_scope.dateHelper.yesterday()).isSame(yesterday, 'minute')).toBe(true);
    });
});

describe('utils.OPAL._track', function(){
    "use strict";


    var location;
    var analytics;
    var mockWindow;

    beforeEach(function(){
        location = jasmine.createSpyObj('location', ['path', 'url']);
        analytics = jasmine.createSpyObj('analytics', ['pageTrack']);
        mockWindow = {
          location: {
            hash: "",
            pathname: ""
          },
        }

        OPAL.tracking.manualTrack = true;
        OPAL.tracking.opal_angular_exclude_tracking_prefix = ['something'];
        OPAL.tracking.opal_angular_exclude_tracking_qs = ['anotherThing/#/'];
    });

    afterEach(function(){
      OPAL.tracking.manualTrack = false;
      OPAL.tracking.opal_angular_exclude_tracking_prefix = [];
      OPAL.tracking.opal_angular_exclude_tracking_qs = [];
    })

    it('should track if not excluded', function(){
      location.path.and.returnValue("please");
      location.url.and.returnValue("please?that=this");
      mockWindow.location.hash = "track_this"
      mockWindow.location.pathname = "/#/please"
      OPAL._track(location, analytics, mockWindow);
      expect(analytics.pageTrack).toHaveBeenCalledWith("please?that=this");
    })

    it('should not track get urls if the url is excluded from tracking', function(){
      mockWindow.location.pathname = "somethingElse"
      mockWindow.location.hash = "/#/"
      OPAL._track(location, analytics, mockWindow);
      expect(analytics.pageTrack).not.toHaveBeenCalled();
    });

    it('should not track the query params if the url is excluding query params from tracking', function(){
      mockWindow.location.pathname = "anotherThing"
      mockWindow.location.hash = "/#/"
      location.path.and.returnValue("anotherThing")
      OPAL._track(location, analytics, mockWindow);
      expect(analytics.pageTrack).toHaveBeenCalledWith('anotherThing');
    });
});

describe("OPAL.module", function(){
  describe('configure modal size', function(){
    var provider;

    beforeEach(module('opal', function($modalProvider){
      provider = $modalProvider;
    }));

    // this is required for the provider to take effect
    beforeEach(inject(function () {}));

    it("should set the modal options to have a size of 'lg'", function(){
      expect(provider.options.size).toEqual('lg');
    });
  });

  describe('configure tracking', function(){
    var previous;

    beforeEach(module('opal', function($cookiesProvider){
      previous = window.OPAL_ANGULAR_EXCLUDE_TRACKING_PREFIX;
    }));

    afterEach(function(){
      window.OPAL_ANGULAR_EXCLUDE_TRACKING_PREFIX = previous;
    });

    it("should set configure tracking", function(){
      window.OPAL_ANGULAR_EXCLUDE_TRACKING_PREFIX = true;
      var config = jasmine.createSpy();
      spyOn(angular, "module").and.returnValue({config: config});
      OPAL.module("someNameSpace");
      expect(config).toHaveBeenCalled();
      var analyticsConfiguration = config.calls.argsFor(0)[0];
      var analyticsProvider = jasmine.createSpyObj(["virtualPageviews"])
      analyticsConfiguration(analyticsProvider);
      expect(analyticsProvider.virtualPageviews).toHaveBeenCalledWith(false);
    });
  });

  describe('dependency registration', function(){
    var implicit_dependencies = [
      'angular-growl',
      'ngCookies',
      'angulartics',
      'angulartics.google.analytics',
      'LocalStorageModule'
    ];

    it('it should add globally scoped dependencies to the ANGULAR DEPS', function(){
      window.OPAL_ANGULAR_DEPS = ["something"];
      var dependencies = ["something-else"];
      spyOn(angular, "module").and.returnValue({config: function(){}});
      expected = dependencies.concat(implicit_dependencies);
      expected.push("something");
      OPAL.module("someNameSpace", dependencies);
      expect(angular.module).toHaveBeenCalledWith(
        "someNameSpace", expected
      );
    });
  });

  describe('should set the default cookie to a year in the future', function(){
    var provider;

    beforeEach(module('opal', function($cookiesProvider){
      provider = $cookiesProvider;
    }));

    // this is required for the provider to take effect
    beforeEach(inject(function () {}));

    it("should set the modal options to have a size of 'lg'", function(){
      expect(provider.defaults.expires.getFullYear()).toEqual(
        new Date().getFullYear() + 1
      );
    });
  });
});
