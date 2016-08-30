describe('Utils.OPAL._run', function (){
    var promiseFun, scope, mock_then, mock_modal, mockWindow, $rootScope;

    beforeEach(function(){
      promiseFun = undefined;
      inject(function($injector){
        $rootScope = $injector.get('$rootScope');
      });
      scope = $rootScope.$new();
      mock_then  = { result: { then: function(x){ promiseFun = x } } };
      mock_modal = { open: function(){ return mock_then } };
      spyOn(mock_modal, 'open').and.callThrough();
      spyOn(mock_then, 'result');
      mockWindow = {location: {pathname: undefined}};
      OPAL._run(scope, {}, mock_modal, mockWindow);
    });

    it('Should add open_modal to the root scope.', function () {
        expect(scope.open_modal).toBeDefined();
    });

    it('Should open a modal with the arguments', function () {
        scope.open_modal('TestCtrl', 'template.html', 'lg', {episode: {}})
        var call_args = mock_modal.open.calls.mostRecent().args[0];
        expect(call_args.controller).toBe('TestCtrl');
        expect(call_args.templateUrl).toBe('template.html');
        expect(call_args.size).toBe('lg');
        expect(call_args.resolve.episode()).toEqual({});
    });

    it('Should set the state to modal then back to normal on completion', function(){
      scope.open_modal('TestCtrl', 'template.html', 'lg', {episode: {}});
      expect(scope.state).toBe('modal');
      promiseFun();
      expect(scope.state).toBe('normal');
    });

    it('Should open a modal when the user has been idle', function(){
      spyOn(scope, "open_modal");
      scope.$emit('IdleStart');
      expect(scope.open_modal).toHaveBeenCalledWith(
        'KeyBoardShortcutsCtrl',
        '/templates/logout_modal.html',
        'lg'
      )
    });

    it('Should log the user out if the user has been logged in too long', function(){
      scope.$emit('IdleTimeout');
      expect(mockWindow.location.pathname).toBe('/accounts/logout/');
    });

    describe('indexOf for IE8', function(){
        beforeEach(function(){
            Array.prototype._indexof = _indexof;
        })

        it('should return the index of the thing', function(){
            expect([1,2,3]._indexof(2)).toEqual(1);
            expect([1,2,3]._indexof(3)).toEqual(2);
            expect([1,2,3]._indexof(0)).toEqual(-1);
        });

    })
});

describe('utils.OPAL._configure', function(){
  beforeEach(function(){
    module('opal');
  });
  it('should configure the relevent modules', function(){
    var testModule = jasmine.createSpyObj('testModule', ['config']);
    OPAL._configure(testModule);
    expect(testModule.config).toHaveBeenCalled();
  });

  describe('it should configure modules', function(){
    beforeEach(function(){
      inject(function($injector){
        Idle = $injector.get('Idle');
      });
    });
  });
});

describe('utils.OPAL._track', function(){
    var location;
    var analytics;

    beforeEach(function(){
        location = jasmine.createSpyObj('location', ['path', 'url']);
        analytics = jasmine.createSpyObj('analytics', ['pageTrack']);
        OPAL._trackingConfig.manualTrack = true;
        OPAL._trackingConfig.opal_angular_exclude_tracking_prefix = ['something'];
        OPAL._trackingConfig.opal_angular_exclude_tracking_qs = ['anotherThing'];
    });

    afterEach(function(){
      OPAL._trackingConfig.manualTrack = false;
      OPAL._trackingConfig.opal_angular_exclude_tracking_prefix = [];
      OPAL._trackingConfig.opal_angular_exclude_tracking_qs = [];
    })

    it('should track if not excluded', function(){
      location.path.and.returnValue("trackThis");
      location.url.and.returnValue("trackThis?that=this");
      OPAL._track(location, analytics);
      expect(analytics.pageTrack).toHaveBeenCalledWith("trackThis?that=this");
    })

    it('should not track get urls if the url is excluded from tracking', function(){
      location.path.and.returnValue("somethingElse");
      OPAL._track(location, analytics);
      expect(analytics.pageTrack).not.toHaveBeenCalled();
    });

    it('should not track the query params if the url is excluding query params from tracking', function(){
      location.url.and.returnValue("anotherThing?something=tree");
      location.path.and.returnValue("anotherThing")
      OPAL._track(location, analytics);
      expect(analytics.pageTrack).toHaveBeenCalledWith('anotherThing');
    });
});
