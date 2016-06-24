describe('episodeVisibility', function(){
    var $scope, episode, episodeVisibility, episodeData;

    var profile = {
        readonly   : false,
        can_extract: true,
        can_see_pid: function(){return true; }
    };

    episodeData = {
        id: 123,
        date_of_admission: "19/11/2013",
        active: true,
        discharge_date: null,
        date_of_episode: null,
        tagging: [{
            mine: true,
            tropical: true
        }],
        demographics: [{
            id: 101,
            first_name: 'John',
            surname: ' Smith',
            date_of_birth: '31/071980',
            hospital_number: '555'
        }],
        location: [{
            category: 'Inepisode',
            hospital: 'UCH',
            ward: 'T10',
            bed: '15',
            date_of_admission: '01/08/2013',
        }],
        diagnosis: [{
            id: 102,
            condition: 'Dengue',
            provisional: true,
            date_of_diagnosis: '20/04/2007'
        }, {
            id: 103,
            condition: 'Malaria',
            provisional: false,
            date_of_diagnosis: '19/03/2006'
        }]
    };


    beforeEach(function(){
        module('opal.services');

        module('opal.services', function($provide) {
            $provide.value('UserProfile', function(){ return profile; });
        });

        inject(function($injector){
            episodeVisibility = $injector.get('episodeVisibility');
        });

        $scope = {
            currentTag: 'micro',
            currentSubTag: 'all',
            query: {
                hospital_number: '',
                ward: ''
            }
        }
        episode = episodeData;
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
