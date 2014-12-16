/**
 * Created by florije on 2014/12/15.
 */

(function () {

    'use strict';

    angular.module('TodoApp', [])
        .run(function ($rootScope) {
            $rootScope.name = 'fuboqing';
        })
        .controller("AppCtrl", function ($scope, $http) {
            $scope.message = "fuboiqng";

            $http.get("/things").success(function (data) {
                $scope.things = data;
            })
        })
}());

//var app = angular.module('myApp', []);

//app.run(function ($rootScope) {
//    $rootScope.name = "florije"
//});