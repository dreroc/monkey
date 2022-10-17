import React from 'react';
import Graph from 'react-graph-vis';
import { getOptions, edgeGroupToColor } from 'components/map/MapOptions';
import { CommunicationTypes, MapNode, OS } from 'components/types/MapNode';

class GraphWrapper extends React.Component {

  constructor(props) {
    super(props);
  }

  generateEdges(mapNodes) {
    let edges = [];
    console.log(mapNodes);
    for (const mapNode of mapNodes) {
      for (const [connected_to, connection_type] of Object.entries(mapNode.connections)) {
        edges.push({
          from: mapNode.machine_id,
          to: connected_to,
          color: edgeGroupToColor(connection_type)
        });
      }
    }

    return edges;
  }

  generateNodes(mapNodes) {
    let nodes = [];
    for (const mapNode of mapNodes) {
      nodes.push({
        id: mapNode.machine_id,
        group: mapNode.calculateNodeGroup(),
        label: mapNode.getLabel()
      });
    }
    return nodes;
  }

  generateGraph(mapNodes) {
    return {
      edges: this.generateEdges(mapNodes),
      nodes: this.generateNodes(mapNodes)
    };
  }

  render() {
    let mapNodes = [
      new MapNode(
        1,
        ['10.10.0.1'],
        true,
        {
          2: CommunicationTypes.exploited,
          3: CommunicationTypes.exploited
        },
        OS.windows,
        'island',
        true,
        true,
        1,
        null
      ),
      new MapNode(
        2,
        ['10.10.0.2'],
        true,
        {
          1: CommunicationTypes.cc,
          3: CommunicationTypes.scan
        },
        OS.linux,
        'lin-1',
        false,
        true,
        2,
        1
      ),
      new MapNode(
        3,
        ['10.10.0.3'],
        true,
        {
          1: CommunicationTypes.cc,
          4: CommunicationTypes.scan
        },
        OS.windows,
        'win-xp',
        false,
        true,
        3,
        1
      ),
      new MapNode(
        4,
        ['10.10.0.4'],
        false,
        { 3: CommunicationTypes.tunnel },
        OS.unknown,
        'lin-2',
        false,
        true,
        null,
        null
      )
    ];
    let options = getOptions();
    let graph = this.generateGraph(mapNodes);
    return (
      <div className={'net-graph-wrapper'}>
        <Graph graph={graph} options={options} events={this.props.events} />
      </div>
    )
  }
}

let ReactiveGraph = GraphWrapper;
export { ReactiveGraph };
