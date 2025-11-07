from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.services.tool_service import ToolService


class ToolGateway:
    """Routes tool invocations to MCP if enabled, otherwise falls back to local ToolService.

    This keeps ChatService and API endpoints agnostic to whether tools are provided locally
    or via an external MCP server.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.tool_service = ToolService()
        self.use_mcp = bool(getattr(self.settings, "USE_MCP", False))

        # Placeholder for a future MCP client instance
        self._mcp_client = None

    async def _ensure_mcp(self) -> None:
        """Lazy-initialize MCP client when USE_MCP is true. Placeholder stub."""
        if not self.use_mcp:
            return
        if self._mcp_client is not None:
            return
        # In a full implementation, connect to MCP server here and assign to self._mcp_client
        # Example: self._mcp_client = await McpClient.connect("ws://localhost:9000")
        pass

    def get_available_tools(self) -> List[Dict[str, Any]]:
        # For now, expose local tools; MCP listing can be added later
        return self.tool_service.get_available_tools()

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        # Try MCP first if enabled (not implemented yet), then local fallback
        if self.use_mcp:
            try:
                await self._ensure_mcp()
                # If implemented, call MCP tool here and return
                # result = await self._mcp_client.call_tool(tool_name, arguments)
                # return result
            except Exception as mcp_error:
                print(f"🔧 MCP error, falling back to local tool: {mcp_error}")

        # Fallback to local ToolService
        return await self.tool_service.execute_tool(tool_name=tool_name, arguments=arguments)


