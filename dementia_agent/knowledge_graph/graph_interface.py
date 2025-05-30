from dementia_agent.knowledge_graph.graph import KnowledgeGraph


class GraphInterface:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph

    def retrieve_information(self, description: str):
        """
        Retrieve information about the elder based on a query.

        Args:
            description (str): The description of the information to retrieve.

        Returns:
            str: The retrieved information.
        """
        print(f"Accessing graph: {self.knowledge_graph}")
        info = input(f"Enter information for {description}: ")
        return info