"""Tests for ExitCallbackHandler."""

import json

from langchain_core.agents import AgentFinish

from cellar_door_exit import ExitMarker, ExitType
from cellar_door_langchain import ExitCallbackHandler


class TestExitCallbackHandler:
    def test_default_construction(self) -> None:
        handler = ExitCallbackHandler()
        assert handler.origin == "langchain"
        assert handler.exit_type == ExitType.VOLUNTARY
        assert len(handler.markers) == 0
        assert handler.max_markers == 1000

    def test_custom_origin(self) -> None:
        handler = ExitCallbackHandler(origin="my-platform")
        assert handler.origin == "my-platform"

    def test_on_chain_end_creates_marker(self) -> None:
        handler = ExitCallbackHandler()
        handler.on_chain_end(outputs={"result": "done"})
        assert len(handler.markers) == 1
        marker = handler.markers[0]
        assert isinstance(marker, ExitMarker)
        assert marker.id.startswith("urn:exit:")
        assert marker.origin == "langchain"

    def test_on_agent_finish_creates_marker(self) -> None:
        handler = ExitCallbackHandler()
        finish = AgentFinish(return_values={"output": "done"}, log="")
        handler.on_agent_finish(finish)
        assert len(handler.markers) == 1

    def test_multiple_chain_ends(self) -> None:
        handler = ExitCallbackHandler()
        for _ in range(5):
            handler.on_chain_end(outputs={})
        assert len(handler.markers) == 5

    def test_max_markers_eviction(self) -> None:
        handler = ExitCallbackHandler(max_markers=3)
        for _ in range(5):
            handler.on_chain_end(outputs={})
        assert len(handler.markers) == 3
        # Oldest should have been evicted
        ids = [m.id for m in handler.markers]
        assert len(set(ids)) == 3  # All unique

    def test_root_only_skips_subchains(self) -> None:
        handler = ExitCallbackHandler(root_only=True)
        # Simulate: root chain > subchain > subchain end > root chain end
        handler.on_chain_start(serialized={}, inputs={})
        handler.on_chain_start(serialized={}, inputs={})  # nested
        handler.on_chain_end(outputs={})  # nested end — should NOT create marker
        assert len(handler.markers) == 0
        handler.on_chain_end(outputs={})  # root end — SHOULD create marker
        assert len(handler.markers) == 1

    def test_root_only_false_fires_on_all(self) -> None:
        handler = ExitCallbackHandler(root_only=False)
        handler.on_chain_start(serialized={}, inputs={})
        handler.on_chain_start(serialized={}, inputs={})
        handler.on_chain_end(outputs={})
        handler.on_chain_end(outputs={})
        assert len(handler.markers) == 2

    def test_on_marker_callback(self) -> None:
        received: list[ExitMarker] = []
        handler = ExitCallbackHandler(on_marker=received.append)
        handler.on_chain_end(outputs={})
        assert len(received) == 1
        assert received[0].id == handler.markers[0].id

    def test_clear(self) -> None:
        handler = ExitCallbackHandler()
        handler.on_chain_end(outputs={})
        assert len(handler.markers) == 1
        handler.clear()
        assert len(handler.markers) == 0

    def test_markers_to_json(self) -> None:
        handler = ExitCallbackHandler()
        handler.on_chain_end(outputs={})
        handler.on_chain_end(outputs={})
        json_str = handler.markers_to_json()
        parsed = json.loads(json_str)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert all("exitType" in m for m in parsed)
        assert all("@context" in m for m in parsed)

    def test_custom_exit_type(self) -> None:
        handler = ExitCallbackHandler(exit_type=ExitType.FORCED)
        handler.on_chain_end(outputs={})
        assert handler.markers[0].exit_type == ExitType.FORCED

    def test_handler_name(self) -> None:
        handler = ExitCallbackHandler()
        assert handler.name == "ExitCallbackHandler"
