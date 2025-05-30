from typing import Protocol, runtime_checkable, Any, Union

from dementia_agent.knowledge_graph.graph import retrieve_information

AllowedParams = (int | float | bool | str | list['AllowedParams'] | dict[str, 'AllowedParams'])

@runtime_checkable
class GeminiFunction(Protocol):
    def __call__(self, *args: AllowedParams, **kwargs: AllowedParams) -> Any:
        """
        This protocol defines the structure for a function callable by the Gemini API. Note that the parameters are
        restricted to some primitive types (int, str, list, bool) to ensure compatibility with the Gemini API's
        function calling.

        For every function, it is also required to have a docstring that describes the function's
        purpose and parameters, along with type hints as shown for this protocol. Unlike this protocol however,
        actual functions should not have ambiguous parameter types.

        Args:
            *args (list[int|str|list|bool]): Positional arguments for the function.
            **kwargs (dict[str, int|str|list|bool]): Keyword arguments for the function.
        """
        ...


__FUNCTION_REGISTRY: dict[str, GeminiFunction] = {}
def register_function(
    function: GeminiFunction,
) -> GeminiFunction:
    """
    Register a function using the decorator.

    Args:
        function (GeminiFunction): The task class to register.
    Returns:
        GeminiFunction: The function.
    """
    if function.__name__ in __FUNCTION_REGISTRY:
        raise ValueError(f"Function '{function.__name__}' is already registered.")
    __FUNCTION_REGISTRY[function.__name__] = function
    return function


def function_from_registry(
    function_name: str,
) -> GeminiFunction:
    """
    Retrieve a function from the registry by its name.

    Args:
        function_name (str): The name of the function to retrieve.

    Returns:
        GeminiFunction: The function if found, otherwise None.
    """
    if __FUNCTION_REGISTRY.get(function_name, None) is None:
        raise ValueError(f"Function '{function_name}' is not registered.")
    return __FUNCTION_REGISTRY[function_name]


def get_functions() -> list[GeminiFunction]:
    """
    Get all registered functions

    Returns:
        dict[str, GeminiFunction]: A dictionary of all registered functions.
    """
    return list(__FUNCTION_REGISTRY.values())


@register_function
def get_information(
    description: str
):
    """
    Retrieve information about the elder based on a query.

    Args:
        description (str): The description of the information to retrieve.

    Returns:
        str: The retrieved information.
    """
    info = retrieve_information(description)
    return info


@register_function
def show_person(
    name: str
) -> bool:
    """
    Show an image of a person.
    Args:
        name (str): The name of the person.
    Returns:
        bool: True if the image was shown, False otherwise.
    """
    print("Show person:", name)
    return True


@register_function
def play_audio(
        audio: str
):
    """
    Play an audio file.

    Args:
        audio (str): A textual Description of the audio to play.

    Returns:
        bool: True if the audio was played successfully, False otherwise.
    """
    print("Playing audio:", audio)
    return True