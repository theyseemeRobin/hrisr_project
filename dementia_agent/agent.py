import gradio as gr
from .gemini.gemini import Gemini
from .gemini.gemini_functions import register_function
from .knowledge_graph.retriever import Retriever


class DementiaAgent:
    def __init__(self, gemini: Gemini, retriever: Retriever):

        self.gemini = gemini
        self.retriever = retriever

        # give gemini access to the graph interface
        register_function(retriever.retrieve_information)

        self.initialized = False
        self.history = []
        self.chat_interface = None
        self.day = None
        self.location = None
        self.system_prompt = None
        self.time = None
        self.chatbot = None
        self.demo = None
        self.create_chat_interface()

    def create_chat_interface(self):

        self.system_prompt = gr.Textbox(
            label="System Instruction",
            value=self.gemini.system_instruction,
            interactive=True,
            lines=20
        )

        self.time = gr.Textbox(
            label="Time",
            value="08:55",
            interactive=True,
            lines=1
        )
        self.location = gr.Textbox(
            label="Location",
            value="Living Room",
            interactive=True,
            lines=1
        )
        self.day = gr.Dropdown(
            label="Day",
            choices=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            value="Monday",
            interactive=True
        )

        with gr.Blocks() as self.demo:
            self.chatbot = gr.Chatbot(placeholder="<strong>Talk with R.O.B.</strong><br>your Social Robot Companion")

            self.chat_interface = gr.ChatInterface(
                fn=self._chat_fn,
                type="messages",
                additional_inputs=[self.system_prompt, self.time, self.location, self.day],
                chatbot=self.chatbot,
                title="R.O.B. the Dementia Agent",
                description="A conversational agent designed to assist with dementia-related queries."
            )

            reset_btn = gr.ClearButton([self.chat_interface, self.chatbot], value="Clear Conversation")
            reset_btn.click(self.reset_chat, None, None, queue=False)

    def reset_chat(self):
        print("Resetting chatbot")
        self.initialized = False
        self.history = []
        self.chatbot.clear()

    def _chat_fn(
            self,
            message: str,
            history: list[dict] = None,
            system_instruction: str = None,
            time: str = None,
            location: str = None,
            day: str = None
    ):
        if not self.initialized:
            try:
                print("Initializing chat with Gemini...")
                self.gemini.system_instruction = system_instruction
                self.gemini.initialize_chat(
                    self.retriever.get_initial_context(
                        time_str=time,
                        day_str=day,
                        location_str=location
                    )
                )
                self.initialized = True
            except Exception as e:
                raise gr.Error(f"Failed to initialize chat: {e}")

        # Get model answer
        response = self.gemini.query(message)

        self.history.append(gr.ChatMessage(role="user", content=message))
        self.history.append(gr.ChatMessage(role="assistant", content=response))

        return response

    def chat(self):
        self.demo.launch()