"""LangChain callback handler for EXIT Protocol departure markers.

Automatically creates EXIT markers when chains or agents complete execution.
"""

from __future__ import annotations

import json
import logging
from collections import deque
from typing import Any, Callable
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentFinish

from cellar_door_exit import (
    ExitMarker,
    ExitType,
    quick_exit,
    to_json,
)

logger = logging.getLogger(__name__)


class ExitCallbackHandler(BaseCallbackHandler):
    """A LangChain callback handler that creates EXIT markers on completion.

    Automatically generates signed departure records when chains or agents
    finish execution.

    Example:
        >>> from cellar_door_langchain import ExitCallbackHandler
        >>> handler = ExitCallbackHandler(origin="my-app")
        >>> # Use with any LangChain chain or agent
        >>> chain.invoke({"input": "hello"}, config={"callbacks": [handler]})
        >>> print(handler.markers[-1].id)  # urn:exit:abc123...

    Args:
        origin: Platform/system name. Defaults to "langchain".
        exit_type: Exit type for auto-generated markers. Defaults to VOLUNTARY.
        on_marker: Called whenever a new marker is created.
        max_markers: Maximum markers to retain in memory. Default 1000.
        root_only: If True (default), only create markers for root-level chain
            completions, not nested subchains. Set to False to get a marker for
            every chain/subchain.
    """

    name: str = "ExitCallbackHandler"

    def __init__(
        self,
        *,
        origin: str = "langchain",
        exit_type: ExitType = ExitType.VOLUNTARY,
        on_marker: Callable[[ExitMarker], None] | None = None,
        max_markers: int = 1000,
        root_only: bool = True,
    ) -> None:
        super().__init__()
        self.origin = origin
        self.exit_type = exit_type
        self.markers: deque[ExitMarker] = deque(maxlen=max_markers)
        self.max_markers = max_markers
        self.root_only = root_only
        self._on_marker = on_marker
        self._chain_depth = 0

    def _record_marker(self) -> ExitMarker:
        """Create and store a new EXIT marker."""
        try:
            result = quick_exit(self.origin, exit_type=self.exit_type)
            marker = result.marker
            self.markers.append(marker)
            if self._on_marker:
                self._on_marker(marker)
            return marker
        except Exception:
            logger.exception("Failed to create EXIT marker")
            raise

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Track chain nesting depth."""
        self._chain_depth += 1

    def on_chain_end(self, outputs: dict[str, Any], **kwargs: Any) -> None:
        """Create an EXIT marker when a chain completes.

        If root_only=True (default), only fires for the outermost chain.
        """
        self._chain_depth = max(0, self._chain_depth - 1)
        if self.root_only and self._chain_depth > 0:
            return
        self._record_marker()

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Create an EXIT marker when an agent finishes."""
        self._record_marker()

    def clear(self) -> None:
        """Remove all stored markers."""
        self.markers.clear()
        self._chain_depth = 0

    def markers_to_json(self) -> str:
        """Export all markers as a JSON array string."""
        return json.dumps(
            [json.loads(to_json(m)) for m in self.markers],
            indent=2,
        )
