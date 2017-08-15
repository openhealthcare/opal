var app = angular.module('opal');

app.config(
    ['$routeProvider',
     function($routeProvider) {
         $routeProvider.when('/list/',{
             controller: 'PatientListRedirectCtrl',
             templateUrl: '/templates/loading_page.html',
             resolve: {
                 metadata: function(Metadata){ return Metadata.load(); }
             }
         }).when('/list/:slug', {
			 controller: 'PatientListCtrl',
			 resolve: {
				 episodedata: function(patientListLoader) { return patientListLoader(); },
                 metadata   : function(Metadata){ return Metadata.load(); },
                 profile    : function(UserProfile){ return UserProfile.load(); }
			 },
			 templateUrl: function(params){
                 var target =  '/templates/patient_list.html';
                 target += '/' + params.slug;
                 return target;
             }
  		 })
             .when('/patient/:patient_id/access_log', {
                 controller: 'PatientRecordAccessLogCtrl',
                 resolve: {
                     patient: function(patientLoader){ return patientLoader(); }
                 },
                 templateUrl: '/templates/patient_record_access_log.html'
             })
             .when('/patient/:patient_id/:view?', {
			     controller: 'PatientDetailCtrl',
                 resolve: {
        				     patient: function(patientLoader) { return patientLoader(); },
                     profile: function(UserProfile){ return UserProfile.load(); },
                     metadata: function(Metadata){ return Metadata.load(); }
                 },
			     templateUrl: function(params){ return '/templates/patient_detail.html' }
             })
             .when('/search', {
			     controller: 'SearchCtrl',
			     templateUrl: '/search/templates/search.html',
             })
             .when('/extract', {
                 controller: 'ExtractCtrl',
                 templateUrl: '/search/templates/extract.html',
                 resolve: {
                     profile: function(UserProfile){ return UserProfile.load(); },
                     schema: function(extractSchemaLoader){ return extractSchemaLoader; },
                     filters: function(filtersLoader){ return filtersLoader(); },
                     referencedata: function(Referencedata){ return Referencedata.load(); }
                 }
             })
             .when('/account', {
                 controller: 'AccountCtrl',
                 templateUrl: '/accounts/templates/account_detail.html'
		     })
             .otherwise({redirectTo: '/'});
     }]);
