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

});
