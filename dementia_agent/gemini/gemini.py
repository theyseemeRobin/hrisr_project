from google import genai
from google.genai import types

from .gemini_functions import get_functions


class Gemini:
    """
    Gemini LLM class.
    """
    def __init__(
            self,
            model: str,
            api_key: str,
            system_instruction: str = None,
    ):
        """
        Constructor of the Gemini LLM class.
        Args:
            model (str): The model to use.
            api_key (str): The API key to use.
            system_instruction (str, optional): The system instruction to use. Defaults to SYSTEM_INSTRUCTIONS.
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.system_instruction = system_instruction
        self.tools = None
        self.tool_config = None
        self.config = None
        self.chat = None


    def initialize_chat(self, chat_context: str = None):
        """
        Start a new chat with Gemini.
        """
        if chat_context:
            self.system_instruction += f"\n{chat_context}"

        self.tool_config = types.ToolConfig(
        )
        self.config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=get_functions(),
            tool_config=self.tool_config,
            temperature=0,

        )
        self.chat = self.client.chats.create(model=self.model, config=self.config)

    def query(self, prompt: str, history: list[dict] = None) -> str:
        """
        Query the Gemini LLM model.
        Args:
            prompt (str): The prompt to give the LLM.

        Returns:
            str: The response.
        """
        response = self.chat.send_message(prompt)
        return response.text