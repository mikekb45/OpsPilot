# OpsPilot - minimal MCP server.
#
# A standalone process exposing tools over the Model Context Protocol,
# instead of as plain Python functions called directly inside
# harness/main.py's harness. Deliberately a separate file: an MCP
# server is meant to be independent of any one client, so this
# duplicates get_queue_status() rather than importing it from there.

from mcp.server.mcpserver import MCPServer
import chromadb

mcp = MCPServer("opspilot")

chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="opspilot_knowledge")


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


@mcp.tool()
def search_knowledge_base(query: str):
    """Searches the OpsPilot knowledge base for guidance on failure modes, escalation paths, and runbook procedures."""
    results = collection.query(query_texts=[query], n_results=3)

    return [
        {"source": metadata["source"], "content": content}
        for metadata, content in zip(results["metadatas"][0], results["documents"][0])
    ]


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
