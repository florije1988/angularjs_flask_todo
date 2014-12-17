/**
 * Created by florije on 2014/12/15.
 */

(function () {

    'use strict';

    angular.module('ThingApp', [])
        .run(function ($rootScope) {
            //$rootScope.name = 'fuboqing';
        })
        .controller("ThingInitController", function ($scope, $http) {
            //$scope.message = "fuboiqng";

            $http.get("/things").success(function (results) {
                $scope.things = results.data;
            });

            $scope.postThing = function () {
                var thing = $scope.input_thing;
                // fire the API request
                $http.post('/things', {"content": thing}).
                    success(function (results) {
                        $scope.things = results.data
                    }).
                    error(function (error) {

                    });
            }
        })
        .controller("ThingNewController", function($scope, $http){

        })
}());

//var app = angular.module('myApp', []);

//app.run(function ($rootScope) {
//    $rootScope.name = "florije"
//});