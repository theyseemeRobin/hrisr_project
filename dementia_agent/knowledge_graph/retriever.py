import logging
import ollama
import time
from build.lib.dementia_agent.knowledge_graph.visualize import visualize_graph
from dementia_agent.knowledge_graph.graph import KnowledgeGraph, NodeType, EventData, PersonData


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
        ollama.pull(embedding_model)
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


    def get_initial_context(
            self,
            time_str: str = "08:55",
            day_str: str = "Monday",
            location_str: str = "Living Room"
    ) -> str:
        """
        Get the initial context of the knowledge graph. This includes the user information.

        Args:
            time_str (str): The current time in HH:MM format.
            day_str (str): The current day of the week (e.g., Monday).
            location_str (str): The location of the user.

        Returns:
            str: The initial context of the knowledge graph.
        """
        try:
            time.strptime(time_str, "%H:%M")
        except Exception as e:
            logging.error(f"Invalid time format: {time_str}. Expected HH:MM format.")
            raise e
        try:
            time.strptime(day_str, "%A")
        except Exception as e:
            logging.error(f"Invalid day format: {day_str}. Expected a valid day of the week (e.g., Monday or monday).")
            raise e

        logging.info("Retrieving initial context from knowledge graph.")
        node_ids = self.knowledge_graph.get_neighbors('user', max_distance=0)
        info = self.knowledge_graph.nodes_to_text(node_ids)
        return (
            f"{time_str}\n"
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

    def add_event(self, node_names: list[str], predicate: str, event: str, description: str, time: str, day: str, location: str)-> str:
        """
        Add an event to the elder's knowledge graph, every node_name participating must be one of the people in retrieve_nodes.
        Always call retrieve_nodes before this function to check whether the node_name participating are in the list of node_name retrieved from retrieve_nodes.

        Args:
            node_names(list[str]): List of node names that participate in the event, every subject participating must be one of the people in retrieve_nodes.
            predicate (str): The predicate (relation), e.g., "likes", "hasChild".
            event (str): The event to be added.
            description (str): The description of the event.
            time (str): The time of the event.
            day (str): The day of the event.
            location (str): The location of the event.

        Returns:
            str: Feedback on success or failure.
        """
        try:
            # Create event
            if event not in self.knowledge_graph._graph:
                self.knowledge_graph.add_event(event, event=EventData(
                    title=event,
                    description=description,
                    time=time,
                    day=day,
                    location=location
                ))

            # Add connections
            for node_name in node_names:
                if node_name in self.knowledge_graph.get_nodes():
                    self.knowledge_graph.connect(node_name, predicate, event)
                    print("Added:", node_name, predicate, event)
            visualize_graph(self.knowledge_graph)
            return f"Successfully added {event} to the knowledge graph"

        except Exception as e:
            logging.exception(f"Failed to add event to knowledge graph: {e}")
            print(f"Failed to add event to knowledge graph. node_names must be one of {self.retrieve_nodes()}")
            return f"Failed to add event to knowledge graph. node_names must be one of {self.retrieve_nodes()}"

    def retrieve_nodes(self) -> list[str]:
        """
        Return list of all existing nodes in the knowledge graph.

        Returns:
            list[str]: The list of existing nodes in the knowledge graph.
        """
        return self.knowledge_graph.get_nodes()

