(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Example-Services-Collection
  * @description Angular resource to fetch /api/service/vaosservice/
  **/
  .service('Example-Services-Collection', function($resource){
    return $resource('/api/service/vaosservice/');
  })
})();