from dataclasses import dataclass, asdict
from enum import Enum, auto
from typing import Dict, Any

import networkx as nx


class NodeType(Enum):
    PERSON = auto()
    EVENT = auto()


@dataclass
class PersonData:
    name: str
    age: int

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


@dataclass
class EventData:
    time: str
    day: str
    title: str
    location: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


class KnowledgeGraph:
    def __init__(self):
        self._graph = nx.MultiDiGraph()

    def add_person(self, id: str, person_data: PersonData):
        self._graph.add_node(id, type=NodeType.PERSON, data=person_data.to_dict())
        return id

    def add_event(self, id: str, event: EventData):
        self._graph.add_node(id, type=NodeType.EVENT, data=event.to_dict())
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