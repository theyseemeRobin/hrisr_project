from .gemini.gemini import Gemini
from .gemini.gemini_functions import register_function
from .knowledge_graph.retriever import Retriever


class DementiaAgent:

    def __init__(self, gemini: Gemini, retriever: Retriever):
        self.gemini = gemini
        self.retriever = retriever

        # give gemini access to the graph interface
        register_function(retriever.retrieve_information)
        register_function(retriever.add_event)
        register_function(retriever.retrieve_nodes)

    def chat(self):
        self.gemini.initialize_chat(self.retriever.get_initial_context())
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