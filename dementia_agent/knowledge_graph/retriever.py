import logging
import random
import time

import ollama

from dementia_agent.knowledge_graph.graph import KnowledgeGraph, NodeType
import time

from dementia_agent.util import get_yes_or_no, get_day, get_time


def cosine_similarity(a, b):
  dot_product = sum([x * y for x, y in zip(a, b)])
  norm_a = sum([x ** 2 for x in a]) ** 0.5
  norm_b = sum([x ** 2 for x in b]) ** 0.5
  return dot_product / (norm_a * norm_b)



class Retriever:
    def __init__(self, knowledge_graph: KnowledgeGraph, embedding_model: str, retrieval_distance: int = 0):
        """
        Initialize the Retriever.
        Args:
            knowledge_graph: The knowledge graph to retrieve information from.
            embedding_model: The name of the ollama embedding model to use for node embeddings.
            retrieval_distance: The distance between a matching node and the adjacent nodes included in the retrieval.
                                With 0, only the matching node is included, while with 1, the matching node and its
                                direct neighbors are included.
        """
        self.knowledge_graph = knowledge_graph
        self.embedding_model = embedding_model
        self.retrieval_distance = retrieval_distance
        self.embeds = {}

    def compute_node_embeddings(self):
        """
        Compute and store embeddings for all nodes in the knowledge graph using the specified embedding model.
        """
        logging.info("Computing node embeddings.")
        nodes = self.knowledge_graph._graph.nodes(data=True)
        nodes = {node_id: self.knowledge_graph.node_to_text(node_id) for node_id, data in nodes if node_id != 'user'}
        for node_id, text in nodes.items():
            embedding = ollama.embed(input=text, model=self.embedding_model)['embeddings'][0]
            self.embeds[node_id] = embedding


    def get_matching_node(self, query: str, top_n: int = 1) -> list[str]:
        """
        Retrieve the top N nodes that match the query based on cosine similarity of their embeddings.
        Args:
            query: The query to match against the node embeddings.
            top_n: The number of top matching nodes to return.
        Returns:
            list: A list of node IDs that match the query, sorted by similarity score.
        """
        if not self.embeds:
            self.compute_node_embeddings()
        query_embed = ollama.embed(input=query, model=self.embedding_model)['embeddings'][0]
        scores = {node_id : cosine_similarity(query_embed, node_embed) for node_id, node_embed in self.embeds.items()}
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        logging.info(
            f"Retrieval scores for query '{query}':\n" +
            "\n".join([ f"{node_id}: {score}" for node_id, score in sorted_nodes])
        )
        return list(zip(*sorted_nodes))[0][:top_n]


    def get_initial_context(self) -> str:
        """
        Get the initial context of the knowledge graph. This includes the user information.

        Returns:
            str: The initial context of the knowledge graph.
        """
        current_time = time.strftime("%H:%M")
        current_day = time.strftime("%A")
        time_str = f"Current time: {current_time}, Current day: {current_day}"
        override_time = get_yes_or_no(f"Override time and day ({time_str})?")
        if override_time:
            current_time = get_time("Enter the current time")
            current_day = get_day("Enter the current day")
            time_str = f"Current time: {current_time}, Current day: {current_day}"

        location = "living room"
        override_location = get_yes_or_no(f"Override location ({location})?")
        if override_location:
            location = input("Enter the current location: ").strip()
        location_str = f"Current location: {location}"

        logging.info("Retrieving initial context from knowledge graph.")
        node_ids = self.knowledge_graph.get_neighbors('user', max_distance=0)
        info = self.knowledge_graph.nodes_to_text(node_ids)
        return (f"{time_str}\n"
                f"{location_str}\n"
                f"User information:\n{info}"
                )

    def retrieve_information(self, query: str, category: str = "") -> str:
        """
        Retrieve information about the elder based on a query.

        Args:
            query: The description of the information to retrieve.
            category: The category of the nodes to search, one of ['PERSON', 'EVENT', '']. '' means all categories.

        Returns:
            str: The retrieved information.
        """

        logging.info(f"Retrieving information for {query}")

        nodes = self.knowledge_graph._graph.nodes(data=True)
        if category:
            nodes = {node_id: data for node_id, data in nodes if data['data'].node_type == NodeType[category.upper()]}
        if not nodes:
            return f"No information found for {query} in category {category}."

        matching_nodes = self.get_matching_node(query, top_n=2)

        info = ""
        for matching_node in matching_nodes:
            neighbors = self.knowledge_graph.get_neighbors(matching_node, max_distance=1)
            node_info = self.knowledge_graph.nodes_to_text(neighbors)
            info += f"Info on {matching_node}:\n{node_info}\n"
        logging.info(info)
        return info