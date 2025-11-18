from mcp.server.fastmcp import FastMCP
from Knn.open_search_ingestion_pipeline import neural_search
from constants import MODEL_ID
from statics_methods import ClientFactory
mcp = FastMCP("Search logs for context in labeling new logs")
client = ClientFactory.get_open_search_client()
@mcp.tool()
async def search_logs(log_message: str, source:str) -> str:
    """Get weather for location."""
    rag= neural_search(log_message, client, MODEL_ID, source,k=3)
    str_rag=str(rag)
    return str_rag

if __name__ == "__main__":
    mcp.run(transport="streamable-http")