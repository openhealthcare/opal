// TODO make this a service
var CATEGORIES = [
    'Inepisode', 'Review', 'Followup', 'Transferred', 'Discharged', 'Deceased'
];

var services = angular.module('opal.services', ['ngResource', 'ngRoute']);
services.config(function($sceProvider){$sceProvider.enabled(false)});
