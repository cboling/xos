(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .service('LogicTopologyHelper', function($window, $log, $rootScope, lodash, serviceTopologyConfig, NodeDrawer){

    var diagonal, nodes, links, i = 0, svgWidth, svgHeight, layout;

    const baseData = {
      name: 'Router',
      type: 'router',
      children: [
        {
          name: 'WAN',
          type: 'network',
          children: [
            {
              name: 'Rack',
              type: 'rack',
              computeNodes: [],
              children: [
                {
                  name: 'LAN',
                  type: 'network',
                  children: [{
                    name: 'Subscriber',
                    type: 'subscriber'
                  }] //subscribers goes here
                }
              ]
            }
          ]
        }
      ]
    };

    /**
     * Calculate the horizontal position for each element.
     * subsrcribers, devices and routers have the same fixed width 20
     * network have a fixed width 104
     * rack have a fixed width 105
     * build and array of 6 elements representing the position of each element in the svg
     * to equally space them
     */

    this.computeElementPosition = (svgWidth) => {

      let xPos = [];

      let totalElWidth = lodash.reduce(serviceTopologyConfig.elWidths, (el, val) => val + el, 0);

      let remainingSpace = svgWidth - totalElWidth - (serviceTopologyConfig.widthMargin * 2);

      let step = remainingSpace / (serviceTopologyConfig.elWidths.length - 1);

      lodash.forEach(serviceTopologyConfig.elWidths, (el, i) => {

        // get half of the previous elements width
        let previousElWidth = 0;
        if(i !== 0){
          previousElWidth = lodash.reduce(serviceTopologyConfig.elWidths.slice(0, i), (el, val) => val + el, 0);
        }

        let elPos =
          serviceTopologyConfig.widthMargin // right margin
          + (step * i) // space between elements
          + (el / 2) // this el width
          + previousElWidth; // previous elements width

        xPos.push(svgWidth - elPos);
      })

      return xPos
    };

    /**
    * from a nested data structure,
    * create nodes and links for a D3 Tree Layout
    */
    const computeLayout = (data) => {
      let nodes = layout.nodes(data);

      // Normalize for fixed-depth.
      nodes.forEach((d) => {
        // position the child node horizontally
        d.y = this.computeElementPosition(svgWidth)[d.depth];
      });

      let links = layout.links(nodes);

      return [nodes, links];
    };

    /**
    * Draw the containing group for any node or update the existing one
    */
    const drawNodes = (svg, nodes) => {
      // Update the nodes…
      var node = svg.selectAll('g.node')
      .data(nodes, d => {
        if(!angular.isString(d.d3Id)){
          d.d3Id = `tree-${++i}`;
        }
        return d.d3Id;
      });

      // Enter any new nodes
      var nodeEnter = node.enter().append('g')
      .attr({
        class: d => `node ${d.type}`,
        transform: `translate(${svgWidth / 2}, ${svgHeight / 2})`
      });

      // create Nodes
      NodeDrawer.addNetworks(node.filter('.network'));
      NodeDrawer.addRack(node.filter('.rack'));
      NodeDrawer.addPhisical(node.filter('.router'));
      NodeDrawer.addPhisical(node.filter('.subscriber'));
      NodeDrawer.addDevice(node.filter('.device'));

      // add event listener to subscriber
      node.filter('.subscriber')
      .on('click', () => {
        $rootScope.$emit('subscriber.modal.open');
      });

      //update nodes
      // TODO if data change, only update them
      // NodeDrawer.updateRack(node.filter('.rack'));

      // Transition nodes to their new position.
      var nodeUpdate = node.transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          'transform': d => `translate(${d.y},${d.x})`
        });

      // TODO handle node remove
    };

    /**
    * Handle links in the tree layout
    */
    const drawLinks = (svg, links) => {

      diagonal = d3.svg.diagonal()
      .projection(d => [d.y, d.x]);

      // Update the links…
      var link = svg.selectAll('path.link')
        .data(links, d => {
          return d.target.d3Id
        });

      // Enter any new links at the parent's previous position.
      link.enter().insert('path', 'g')
        .attr('class', d => `link ${d.target.type}`)
        .attr('d', function(d) {
          var o = {x: svgHeight / 2, y: svgWidth / 2};
          return diagonal({source: o, target: o});
        });

      // Transition links to their new position.
      link.transition()
        .duration(serviceTopologyConfig.duration)
        .attr('d', diagonal);
    };

    /**
    * Calculate the svg size and setup tree layout
    */
    this.setupTree = (svg) => {
      

      svgWidth = svg.node().getBoundingClientRect().width;
      svgHeight = svg.node().getBoundingClientRect().height;

      const width = svgWidth - (serviceTopologyConfig.widthMargin * 2);
      const height = svgHeight - (serviceTopologyConfig.heightMargin * 2);

      layout = d3.layout.tree()
      .size([height, width]);
    };

    /**
    * Update the tree layout
    */

    this.updateTree = (svg) => {
      // Compute the new tree layout.
      [nodes, links] = computeLayout(baseData);

      drawNodes(svg, nodes);
      drawLinks(svg, links);
    }

    /**
    * Add Subscribers to the tree
    */
    this.addSubscribers = (subscribers) => {

      subscribers.map((subscriber) => {
        subscriber.children = subscriber.devices;
      });

      // add subscriber to data tree
      baseData.children[0].children[0].children[0].children = subscribers;
      
      return baseData;
    };

    /**
    * Add compute nodes to the rack element
    */
   
    this.addComputeNodes = (computeNodes) => {
      baseData.children[0].children[0].computeNodes = computeNodes;
    };

    this.getInstanceStatus = (instances) => {

      const computeNodes = baseData.children[0].children[0].computeNodes;

      // unselect all
      computeNodes.map((node) => {
        node.instances.map((instance) => {
          instance.selected = false
          return instance;
        });
      });

      lodash.forEach(instances, (instance) => {
        computeNodes.map((node) => {
          node.instances.map((d3instance) => {
            if(d3instance.id === instance.id){
              d3instance.selected = true;
            }
            return d3instance;
          });
        });
      });

    }
  });

}());