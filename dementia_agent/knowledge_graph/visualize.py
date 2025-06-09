import json
from pyvis.network import Network
import os

from dementia_agent.knowledge_graph.graph import NodeType


def visualize_graph(
    graph,
    output_file: str = 'graph.html',
    height: str = '750px',
    width: str = '100%',
    directed: bool = True,
    node_font_size: int = 14,
    edge_font_size: int = 12,
    node_distance: int = 200,
    physics: bool = True
) -> None:
    """
    Generate an interactive HTML visualization of the knowledge graph
    using PyVis. Saves to `output_file` with distinct styles for node types,
    edge labels, and customizable display parameters.

    Parameters:
    - node_font_size: Font size for node labels.
    - edge_font_size: Font size for edge labels.
    - node_distance: Approximate distance between nodes (in pixels).
    - physics: Enable or disable physics simulation.
    """
    net = Network(
        height=height,
        width=width,
        directed=directed,
        notebook=False
    )

    # Apply physics options
    if physics:
        net.force_atlas_2based()
    else:
        net.toggle_physics(False)

    # Define styles per node type
    style_map = {
        NodeType.PERSON: {'shape': 'dot', 'color': '#97C2FC'},
        NodeType.EVENT: {'shape': 'box', 'color': '#FFA807'}
    }

    # Add nodes with customizable font size and distinct styles
    for n, attrs in graph._graph.nodes(data=True):
        payload = attrs['data'].to_dict()
        ntype = payload.pop('node_type')
        label = payload.get('name') or payload.get('title') or str(n)
        title = json.dumps(payload, indent=2)
        style = style_map.get(ntype, {})
        net.add_node(
            n,
            label=label,
            title=title,
            shape=style.get('shape'),
            color=style.get('color'),
            font={'size': node_font_size}
        )

    # Add edges with customizable font size
    for u, v, key, eattrs in graph._graph.edges(keys=True, data=True):
        relation = eattrs.get('relation')

        # Check if either node is an event
        u_type = graph._graph.nodes[u]['data'].node_type
        v_type = graph._graph.nodes[v]['data'].node_type
        is_event_edge = (u_type == NodeType.EVENT or v_type == NodeType.EVENT)

        # Determine edge width
        width = 2 if 'user' in (str(u), str(v)) else 0.7

        edge_style = {
            'color': '#FFA500',  # orange for event edges
        } if is_event_edge else {}

        net.add_edge(
            u,
            v,
            label=relation,
            title=relation,
            width=width,
            font={'size': edge_font_size},
            smooth={'enabled': True, 'type': 'curvedCW', 'roundness': 0.2},
            **edge_style
        )

    # Adjust layout distance
    net.repulsion(node_distance=node_distance)

    try:
        net.write_html(output_file, notebook=False, open_browser=False)
        abs_path = os.path.abspath(output_file)
        print(f"Graph saved to {abs_path}\nClick this link to view: file://{abs_path}")
    except Exception as e:
        print(f"Failed to generate visualization: {e}")