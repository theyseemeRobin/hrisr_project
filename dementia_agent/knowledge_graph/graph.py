import abc
from dataclasses import dataclass, asdict
from enum import Enum, auto
from typing import Dict, Any

import networkx as nx


class NodeType(Enum):
    PERSON = auto()
    EVENT = auto()

@dataclass
class NodeData:
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_text(self) -> str:
        data = self.to_dict()

        if 'node_type' in data:
            del data['node_type']
        misc = data.pop('misc')
        if misc is not None:
            data.update(misc)

        misc_str = ', '.join(f"{k}: {v}" for k, v in data.items())
        return misc_str



@dataclass
class PersonData(NodeData):
    name: str
    age: int
    misc: Dict[str, Any] = None
    node_type: NodeType = NodeType.PERSON


@dataclass
class EventData(NodeData):
    title: str
    description: str
    time: str
    day: str
    location: str
    misc: Dict[str, Any] = None
    node_type: NodeType = NodeType.EVENT


class KnowledgeGraph:
    def __init__(self):
        self._graph = nx.MultiDiGraph()

    def add_person(self, id: str, person_data: PersonData):
        self._graph.add_node(id, data=person_data)
        return id

    def add_event(self, id: str, event: EventData):
        self._graph.add_node(id, data=event)
        return id

    def connect(self, src: str, relation: str, dest: str, bidirectional: bool = False):
        self._graph.add_edge(src, dest, relation=relation)
        if bidirectional:
            self._graph.add_edge(dest, src, relation=relation)

    @classmethod
    def from_config(cls, people: dict[str, PersonData], events: dict[str, EventData], connections: list[tuple[str, str,
    str]]):
        kg = KnowledgeGraph()
        for id, person in people.items():
            kg.add_person(id, person)
        for id, event in events.items():
            kg.add_event(id, event)

        for connection in connections:
            kg.connect(*connection)
        return kg

    def nodes_as_text(self):
        node_ids = self._graph.nodes
        return {node_id: self.node_to_text(node_id) for node_id in node_ids}

    def node_to_text(self, node_id):
        text = self._graph.nodes[node_id]['data'].to_text()
        text += '\n'
        for neighbour_id, edges_data in self._graph.adj[node_id].items():
            for edge_data in edges_data.values():
                text += f"{edge_data['relation']} {neighbour_id}\n"
        return text

    def get_neighbors(self, source: str, max_distance: int =1):
        return list(nx.single_source_shortest_path_length(self._graph, source, cutoff=max_distance).keys())