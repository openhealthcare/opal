describe('episodeVisibility', function(){
    "use strict";

    var $scope, episode, episodeVisibility, opalTestHelper;
    var $rootScope;



    beforeEach(function(){
      module('opal.services');
      module('opal.test');
      inject(function($injector){
        episodeVisibility = $injector.get('episodeVisibility');
        $rootScope = $injector.get('$rootScope');
        opalTestHelper = $injector.get('opalTestHelper');
      });

      $scope = {
        currentTag: 'micro',
        currentSubTag: 'all',
        query: {
            hospital_number: '',
            ward: ''
        }
      }
      episode = opalTestHelper.newEpisode($rootScope);
    });

    it('should allow inactive episodes on mine', function(){
        episode.active = false;
        $scope.currentTag = 'mine';
        expect(episodeVisibility(episode, $scope)).toBe(true);
    });
    it('should allow inactive episodes', function(){
        episode.active = false;
        expect(episodeVisibility(episode, $scope)).toBe(true);
    });
    it('should reject if the hospital number filter fails', function(){
        $scope.currentTag = 'tropical';
        $scope.query.hospital_number = '123'
        expect(episodeVisibility(episode, $scope)).toBe(false);
    });

    it('should include the hospital number if the filter passes', function(){
      $scope.currentTag = 'tropical';
      $scope.query.hospital_number = '1111111111'
      expect(episodeVisibility(episode, $scope)).toBe(true);
    });

    it('should allow if the hospital number filter passes', function(){
        $scope.currentTag = 'tropical';
        expect(episodeVisibility(episode, $scope)).toBe(true);
    });
    it('should reject if the name filter fails', function(){
        $scope.currentTag = 'tropical';
        $scope.query.name = 'Fake Name';
        expect(episodeVisibility(episode, $scope)).toBe(false);
    });
    it('should allow if the name filter passes', function(){
        $scope.currentTag = 'tropical';
        $scope.query.name = 'john'
        expect(episodeVisibility(episode, $scope)).toBe(true);
    });
    it('should allow if unfiltered', function(){
        expect(episodeVisibility(episode, $scope)).toBe(true);
    });
    it('should allow if the bed filter passes', function(){
        $scope.query.bed = '15'
        expect(episodeVisibility(episode, $scope)).toBe(true);
    });
    it('should allow if the bed rangefilter passes', function(){
        $scope.query.bed = '10-20'
        expect(episodeVisibility(episode, $scope)).toBe(true);
    });
    it('should fail if the bed filter fails', function(){
        $scope.query.bed = '14'
        expect(episodeVisibility(episode, $scope)).toBe(false);
    });
    it('should fail if the bed range filter fails', function(){
        $scope.query.bed = '1-10'
        expect(episodeVisibility(episode, $scope)).toBe(false);
    });
    it('should fail fi the ward filter fails', function() {
        $scope.query.ward = 'T8';
        expect(episodeVisibility(episode, $scope)).toBe(false);
    });
});
