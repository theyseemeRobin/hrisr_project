from .knowledge_graph.graph import KnowledgeGraph
from .gemini.gemini import Gemini
from .gemini.gemini_functions import register_function
from .knowledge_graph.graph_interface import GraphInterface


class DementiaAgent:

    def __init__(self, gemini: Gemini, graph_interface: GraphInterface):
        self.gemini = gemini
        self.graph_interface = graph_interface

        # give gemini access to the graph interface
        register_function(graph_interface.retrieve_information)

    def chat(self):
        self.gemini.initialize_chat()
        print(
            f"Starting conversation with Gemini model: {self.gemini.model}\n"
            f"To exit the conversation, type 'quit()'"
        )
        query = ""
        while query != "quit()":
            query = input("You: ")
            if query == "quit()":
                break
            response = self.gemini.query(query)
            print(f"Gemini: {response.text}")