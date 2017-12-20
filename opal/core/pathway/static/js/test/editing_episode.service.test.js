describe('EditingEpisode', function(){
  "use strict";
  var opalTestHelper, EditingEpisode, EditingHelper;
  var $rootScope, editingEpisode, helper;

  beforeEach(function(){
    module('opal.services');
    module('opal.test');
    inject(function($injector) {
      opalTestHelper = $injector.get('opalTestHelper');
      EditingEpisode = $injector.get('EditingEpisode');
      $rootScope = $injector.get('$rootScope');
    });
    editingEpisode = new EditingEpisode();
    helper = editingEpisode.helper;
  });

  describe('EditingHelper', function(){
    it('should remove from the parent', function(){
      editingEpisode.greeting = [
        {
          name: 'hello'
        },
        {
          name: 'bonjour'
        }
      ];

      helper.remove('greeting', 0);
      expect(editingEpisode.greeting).toEqual([{name: 'bonjour'}]);
    });

    it('should record if a subrecord has been populated', function(){
      var someRecord = {
        $someAngluarVar: "as",
        _client: {completed: false},
        greeting: 'hello'
      }
      expect(editingEpisode.helper.isRecordFilledIn(someRecord)).toBe(true);
    });

    it('should record if a subrecord has not been populated', function(){
      var someRecord = {
        $someAngluarVar: "as",
        _client: {completed: false},
      }
      expect(editingEpisode.helper.isRecordFilledIn(someRecord)).toBe(false);
    });

    it('should create a new subrecord from the episode', function(){
      var episode = opalTestHelper.newEpisode($rootScope);
      var beforeDiagnosisLength = episode.diagnosis.length;
      editingEpisode = new EditingEpisode(episode);
      editingEpisode.helper.addRecord('diagnosis');
      expect(editingEpisode.diagnosis.length).toBe(beforeDiagnosisLength + 1);
    });

    it('should create a new subrecord without an episode', function(){
      editingEpisode.helper.addRecord('diagnosis');
      expect(editingEpisode.diagnosis.length).toBe(1);
      expect(!!_.last(editingEpisode.diagnosis)._client).toBe(true);
    });
  });

  describe("EditingEpisode constructor", function(){
    it('should populate the episode', function(){
      var demographics = jasmine.createSpyObj(["makeCopy"]);
      demographics.makeCopy.and.returnValue({first_name: "Wilma"});
      var treatment = jasmine.createSpyObj(["makeCopy"]);
      treatment.makeCopy.and.returnValue({drug: "aspirin"});
      $rootScope.fields = {
        demographics: {single: true},
        treatment: {single: false},
        antimicrobials: {single: false}
      };
      var episode = {demographics: [demographics], antimicrobials: [], treatment: [treatment]};
      var editingEpisode = new EditingEpisode(episode);
      expect(editingEpisode.demographics).toEqual({first_name: "Wilma"});
      expect(editingEpisode.antimicrobials).toEqual([]);
      expect(editingEpisode.treatment).toEqual( [{drug: "aspirin"}]);
      expect(demographics.makeCopy).toHaveBeenCalledWith();
      expect(treatment.makeCopy).toHaveBeenCalledWith();
    });

    it('should allow no episode to be set', function(){
      var editingEpisode = new EditingEpisode();
      // we want to make sure nothing has been hoisted apart from
      // the helper
      var keys = _.filter(_.keys(editingEpisode), function(x){
        return x !==  'helper';
      });
      expect(keys).toEqual([]);
    });
  });


});
