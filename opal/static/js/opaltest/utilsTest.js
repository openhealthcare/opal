describe('Utils.OPAL._run', function (){

    it('Should add open_modal to the root scope.', function () {
        var mock_scope = { $on: function(){} };
        var mock_modal = { open: function(){} };

        OPAL._run(mock_scope, {}, mock_modal)

        expect(mock_scope.open_modal).toBeDefined();
    });

    it('Should open a modal with the arguments', function () {
        var mock_scope = { $on: function(){} };
        var mock_then  = { result: { then: function(){} } };
        var mock_modal = { open: function(){ return mock_then } };
        spyOn(mock_modal, 'open').and.callThrough();
        spyOn(mock_then, 'result');

        OPAL._run(mock_scope, {}, mock_modal)
        mock_scope.open_modal('TestCtrl', 'template.html', 'lg', {episode: {}})

        var call_args = mock_modal.open.calls.mostRecent().args[0];

        expect(call_args.controller).toBe('TestCtrl');
        expect(call_args.templateUrl).toBe('template.html');
        expect(call_args.size).toBe('lg');
        expect(call_args.resolve.episode()).toEqual({});
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

describe('utils.OPAL._track', function(){
    var location;
    var analytics;

    beforeEach(function(){
        location = jasmine.createSpyObj('location', ['path', 'url']);
        analytics = jasmine.createSpyObj('analytics', ['pageTrack']);

        OPAL.tracking.manualTrack = true;
        OPAL.tracking.opal_angular_exclude_tracking_prefix = ['something'];
        OPAL.tracking.opal_angular_exclude_tracking_qs = ['anotherThing'];
    });

    afterEach(function(){
      OPAL.tracking.manualTrack = false;
      OPAL.tracking.opal_angular_exclude_tracking_prefix = [];
      OPAL.tracking.opal_angular_exclude_tracking_qs = [];
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
