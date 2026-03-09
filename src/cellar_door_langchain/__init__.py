"""cellar-door-langchain -- LangChain integration for EXIT Protocol.

Provides a callback handler that automatically creates EXIT markers
when LangChain chains or agents complete execution.

Example:
    >>> from cellar_door_langchain import ExitCallbackHandler
    >>> handler = ExitCallbackHandler(origin="my-app")
    >>> chain.invoke({"input": "hello"}, config={"callbacks": [handler]})
    >>> assert len(handler.markers) > 0
"""

from .handler import ExitCallbackHandler

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "ExitCallbackHandler",
]
