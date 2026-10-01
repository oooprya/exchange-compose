import types

import pytest

from ai.assistant import Assistant


@pytest.mark.asyncio
async def test_chat_submits_all_function_outputs(monkeypatch):
    calls = []

    async def fake_execute_tool(name, arguments):
        return {"name": name, "arguments": arguments}

    class FakeResponses:
        async def create(self, **kwargs):
            calls.append(kwargs)
            if "previous_response_id" in kwargs:
                return types.SimpleNamespace(output_text="done")
            return types.SimpleNamespace(
                id="resp_1",
                output=[
                    types.SimpleNamespace(
                        type="function_call",
                        name="get_rate",
                        call_id="call_1",
                        arguments='{"currency": "USD"}',
                    ),
                    types.SimpleNamespace(
                        type="function_call",
                        name="find_offer",
                        call_id="call_2",
                        arguments='{"currency": "USD", "amount": 100, "operation": "buy"}',
                    ),
                ],
            )

    monkeypatch.setattr("ai.assistant.client",
                        types.SimpleNamespace(responses=FakeResponses()))
    monkeypatch.setattr("ai.assistant.execute_tool", fake_execute_tool)

    assistant = Assistant()
    result = await assistant.chat([{"role": "user", "content": "hello"}])

    assert result == "done"
    assert len(calls) == 2
    assert calls[1]["previous_response_id"] == "resp_1"
    assert calls[1]["input"] == [
        {"type": "function_call_output", "call_id": "call_1",
            "output": '{"name": "get_rate", "arguments": {"currency": "USD"}}'},
        {"type": "function_call_output", "call_id": "call_2",
            "output": '{"name": "find_offer", "arguments": {"currency": "USD", "amount": 100, "operation": "buy"}}'},
    ]
