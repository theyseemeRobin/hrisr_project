import logging
import random
import ollama

from dementia_agent.knowledge_graph.graph import KnowledgeGraph, NodeType


def cosine_similarity(a, b):
  dot_product = sum([x * y for x, y in zip(a, b)])
  norm_a = sum([x ** 2 for x in a]) ** 0.5
  norm_b = sum([x ** 2 for x in b]) ** 0.5
  return dot_product / (norm_a * norm_b)



class Retriever:
    def __init__(self, knowledge_graph: KnowledgeGraph, embedding_model):
        self.knowledge_graph = knowledge_graph
        self.embedding_model = embedding_model
        self.embeds = {}

    def compute_node_embeddings(self):
        logging.info("Computing node embeddings.")
        nodes = self.knowledge_graph._graph.nodes(data=True)
        nodes = {node_id: data['data'].to_text() for node_id, data in nodes}
        for node_id, text in nodes.items():
            embedding = ollama.embed(input=text, model=self.embedding_model)['embeddings'][0]
            self.embeds[node_id] = embedding


    def get_matching_node(self, query, top_n=1):
        if not self.embeds:
            self.compute_node_embeddings()
        query_embed = ollama.embed(input=query, model=self.embedding_model)['embeddings'][0]
        scores = {node_id : cosine_similarity(query_embed, node_embed) for node_id, node_embed in self.embeds.items()}
        sorted_nodes = sorted(scores, key=scores.get, reverse=True)
        logging.info(f"nodes sorted by score: {sorted_nodes}")
        return sorted_nodes[:top_n]


    def get_initial_context(self) -> str:
        """
        Get the initial context of the knowledge graph.

        Returns:
            str: The initial context of the knowledge graph.
        """
        logging.info("Retrieving initial context from knowledge graph.")
        info = self.knowledge_graph.node_to_text('user')
        return f"User information:\n{info}"

    def retrieve_information(self, query: str, category: str = "") -> str:
        """
        Retrieve information about the elder based on a query.

        Args:
            query (str): The description of the information to retrieve.
            category (str, optional): The category of the nodes to search. E.g. "person" or "event". default means all
                                      categories.

        Returns:
            str: The retrieved information.
        """

        logging.info(f"Retrieving information for {query}")

        nodes = self.knowledge_graph._graph.nodes(data=True)
        if category:
            nodes = {node_id: data for node_id, data in nodes if data['data'].node_type == NodeType[category.upper()]}
        if not nodes:
            return f"No information found for {query} in category {category}."

        matching_nodes = self.get_matching_node(query, top_n=1)

        info = ""
        for matching_node in matching_nodes:
            neighbors = self.knowledge_graph.get_neighbors(matching_node, max_distance=1)
            node_info = [self.knowledge_graph.node_to_text(node_id) for node_id in neighbors]
            node_info = '\n'.join(node_info)
            info += f"Info on {matching_node}:\n{node_info}\n"
        logging.info(info)
        return info