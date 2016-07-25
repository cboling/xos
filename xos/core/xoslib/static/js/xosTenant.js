"use strict";angular.module("xos.tenant",["ngResource","ngCookies","ui.router","xos.helpers"]).config(["$stateProvider",function(e){e.state("site-list",{url:"/",template:"<site-list></site-list>"}).state("site",{url:"/site/:id",template:"<site-detail></site-detail>"}).state("createslice",{url:"/site/:site/slice/:id?",template:"<create-slice></create-slice>"})}]).config(["$httpProvider",function(e){e.interceptors.push("NoHyperlinks")}]).directive("siteList",function(){return{restrict:"E",scope:{},bindToController:!0,controllerAs:"vm",templateUrl:"templates/users-list.tpl.html",controller:["Sites","SlicesPlus",function(e,t){var i=this;this.tableConfig={columns:[{label:"Site",prop:"name",link:function(e){return"#/site/"+e.id}},{label:"Allocated",prop:"instance_total"},{label:"Ready",prop:"instance_total_ready"}]},e.query().$promise.then(function(e){return i.sites=e,t.query().$promise}).then(function(e){i.slices=e,i.site_list=i.returnData(i.sites,i.slices)})["catch"](function(e){throw new Error(e)}),this.returnData=function(e,t){var i,s=0,l=[];for(i=0;i<e.length;i++){var n=0,a=0;for(s=0;s<t.length;s++)null!=e[i].id&&null!=t[s].site&&e[i].id===t[s].site&&(n+=t[s].instance_total,a+=t[s].instance_total_ready);var o={id:e[i].id,name:e[i].name,instance_total:n,instance_total_ready:a};l.push(o)}return l}}]}}),angular.module("xos.tenant").run(["$templateCache",function(e){e.put("templates/createslice.html",'<!--<xos-table config="cs.tableConfig" data="cs.sites"></xos-table>-->\n<h2>Slice Details</h2>\n<hr></hr>\n<xos-form ng-model="cs.model" config="cs.config" ></xos-form>\n\n<!--<pre>-->\n<!--&lt;!&ndash;{{cs.users | json}}&ndash;&gt;-->\n\n<!--{{cs.users.name | json}}-->\n\n<!--</pre>-->'),e.put("templates/slicelist.html",'<!--<span ng-bind="siteNameSe"></span>-->\n<!--<xos-field></xos-field>-->\n<a class="addlink btn btn-info" ui-sref="createslice({site: sl.siteId})"><i class="glyphicon glyphicon-plus-sign"></i> Create Slice</a>\n<xos-table config="sl.tableConfig" data="sl.sliceList"></xos-table>\n<!--<div ui-view="sliceDetails"></div>-->\n<!--<pre>{{sl.users[0].site}}</pre>-->\n'),e.put("templates/users-list.tpl.html",'<xos-table config="vm.tableConfig" data="vm.site_list"></xos-table>')}]),angular.module("xos.tenant").directive("siteDetail",function(){return{restrict:"E",scope:{},bindToController:!0,controllerAs:"sl",templateUrl:"templates/slicelist.html",controller:["SlicesPlus","$stateParams",function(e,t){var i=this;this.siteId=t.id,this.tableConfig={columns:[{label:"Slice List",prop:"name",link:function(e){return"#/site/"+e.site+"/slice/"+e.id}},{label:"Allocated",prop:"instance_total"},{label:"Ready",prop:"instance_total_ready"}]},e.query({site:t.id}).$promise.then(function(e){i.sliceList=e})["catch"](function(e){throw new Error(e)})}]}}),angular.module("xos.tenant").directive("createSlice",function(){return{restrict:"E",scope:{},bindToController:!0,controllerAs:"cs",templateUrl:"templates/createslice.html",controller:["Slices","SlicesPlus","Sites","Images","$stateParams","$http","$state","$q","XosUserPrefs","_",function(e,t,i,s,l,n,a,o,r,c){var d=this;this.config={exclude:["site","password","last_login","mount_data_sets","default_flavor","creator","exposed_ports","networks","omf_friendly","omf_friendly","no_sync","no_policy","lazy_blocked","write_protect","deleted","backend_status","backend_register","policed","enacted","updated","created","validators","humanReadableName"],formName:"SliceDetails",feedback:{show:!1,message:"Form submitted successfully !!!",type:"success"},actions:[{label:"Save",icon:"ok",cb:function(e,t){f(e,t).then(function(){a.go("site",{id:d.model.site})})},"class":"success"},{label:"Save and continue editing",icon:"ok",cb:function(e,t){f(e,t)},"class":"primary"},{label:"Save and add another",icon:"ok",cb:function(e,t){f(e,t).then(function(){a.go("createslice",{site:d.model.site,id:""})})},"class":"primary"}],fields:{site:{label:"Site",type:"select",validators:{required:!0},hint:"The Site this Slice belongs to",options:[]},name:{label:"Name",type:"string",hint:"The Name of the Slice",validators:{required:!0,custom:function(e){if(d.model.site){var t=c.find(d.config.fields.site.options,["id",d.model.site]);if(t&&e)return 0===e.toLowerCase().indexOf(t.label.toLowerCase())}return!1}}},serviceClass:{label:"ServiceClass",type:"select",validators:{required:!0},hint:"The Site this Slice belongs to",options:[{id:1,label:"Best effort"}]},enabled:{label:"Enabled",type:"boolean",hint:"Status for this Slice"},description:{label:"Description",type:"string",hint:"High level description of the slice and expected activities",validators:{required:!1,minlength:10}},service:{label:"Service",type:"select",validators:{required:!1},options:[{id:0,label:"--------"}]},slice_url:{label:"Slice url",type:"string",validators:{required:!1,minlength:10}},max_instances:{label:"Max Instances",type:"number",validators:{required:!1,min:0}},default_isolation:{label:"Default Isolation",type:"select",validators:{required:!1},options:[{id:"vm",label:"Virtual Machine"},{id:"container",label:"Container"},{id:"container_vm",label:"Container in VM"}]},default_image:{label:"Default image",type:"select",validators:{required:!1},options:[]},network:{label:"Network",type:"select",validators:{required:!1},options:[{id:"default",label:"Default"},{id:"host",label:"Host"},{id:"bridged",label:"Bridged"},{id:"noauto",label:"No Automatic Networks"}]}}};var u;s.query().$promise.then(function(e){d.users=e,u=d.users,d.optionValImg=d.setData(u,{field1:"id",field2:"name"}),d.config.fields.default_image.options=d.optionValImg})["catch"](function(e){throw new Error(e)}),this.setData=function(e,t){var i,s=[];for(i=0;i<e.length;i++){var l={id:e[i][t.field1],label:e[i][t.field2]};s.push(l)}return s},l.id?(delete this.config.fields.site,this.config.exclude.push("site"),e.get({id:l.id}).$promise.then(function(e){d.users=e,u=e,d.model=u})["catch"](function(e){throw new Error(e)})):(this.model={},r.getUserDetailsCookie().$promise.then(function(e){d.model.creator=e.current_user_id})["catch"](function(e){throw new Error(e)}),i.query().$promise.then(function(e){d.users_site=e,d.optionVal=d.setData(d.users_site,{field1:"id",field2:"name"}),d.config.fields.site.options=d.optionVal})["catch"](function(e){throw new Error(e)}));var f=function(t,i){var s=o.defer();if(delete t.networks,i.$valid){if(t.id)var l=e.update(t).$promise;else var l=e.save(t).$promise;l.then(function(e){d.model=e,d.config.feedback.show=!0,s.resolve(e)})["catch"](function(e){d.config.feedback.show=!0,d.config.feedback.type="danger",e.data&&e.data.detail?d.config.feedback.message=e.data.detail:d.config.feedback.message=e.statusText,s.reject(e)})}return s.promise}}]}}),angular.module("xos.tenant").run(["$location",function(e){e.path("/")}]);