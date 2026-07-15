import sys
from contextlib import AsyncExitStack
from dataclasses import dataclass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass
class ToolSchema:
    name: str
    description: str
    input_schema: dict
    server: str


class MCPClient:
    """Generic async wrapper around the official MCP Python SDK's stdio client.

    Connects to every server listed in `servers` (each a {"name": ..., "command": [...]}
    dict from config.yaml's `mcp.servers`), and exposes a single, server-agnostic
    list_tools()/call_tool() interface so the agent loop never needs to know which
    physical server owns which tool.
    """

    def __init__(self, servers: list):
        self._server_specs = servers
        self._sessions = {}
        self._tool_owner = {}
        self._stack = None

    async def __aenter__(self):
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        for spec in self._server_specs:
            command, *args = spec["command"]
            # Run MCP servers with the same interpreter driving the agent, not
            # whatever "python"/"python3" resolves to on PATH — otherwise a
            # server subprocess can silently miss the venv's dependencies.
            if command in ("python", "python3"):
                command = sys.executable
            params = StdioServerParameters(command=command, args=args)
            read, write = await self._stack.enter_async_context(stdio_client(params))
            session = await self._stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self._sessions[spec["name"]] = session
        return self

    async def __aexit__(self, *exc_info):
        await self._stack.__aexit__(*exc_info)

    async def list_tools(self) -> list:
        schemas = []
        for server_name, session in self._sessions.items():
            result = await session.list_tools()
            for tool in result.tools:
                schemas.append(
                    ToolSchema(
                        name=tool.name,
                        description=tool.description or "",
                        input_schema=tool.inputSchema or {},
                        server=server_name,
                    )
                )
                self._tool_owner[tool.name] = server_name
        return schemas

    async def call_tool(self, name: str, arguments: dict) -> str:
        server_name = self._tool_owner.get(name)
        if server_name is None:
            raise ValueError(f"Unknown tool: {name}")
        session = self._sessions[server_name]
        result = await session.call_tool(name, arguments=arguments)
        parts = []
        for content in result.content:
            parts.append(content.text if hasattr(content, "text") else str(content))
        return "\n".join(parts)
