# OpsPilot - minimal MCP server.
#
# A standalone process exposing tools over the Model Context Protocol,
# instead of as plain Python functions called directly inside
# harness/main.py's harness. Deliberately a separate file: an MCP
# server is meant to be independent of any one client, so this
# duplicates get_queue_status() rather than importing it from there.

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("opspilot")


@mcp.tool()
def get_queue_status():
    """Returns the current status of the order queue."""
    return {
        "queue_name": "OrderQueue",
        "depth": 42,
        "status": "Processing",
    }


@mcp.tool()
def get_recent_errors():
    """Returns a list of recent errors in the order queue."""
    return [
        {"service": "PaymentService", "message": "Payment failed for order 1234", "count": 3},
        {"service": "InventoryService", "message": "Item out of stock for order 5678", "count": 2},
    ]


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
