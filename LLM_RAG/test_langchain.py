import asyncio
from dotenv import load_dotenv
import httpx
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
# NEW/CORRECT CODE:
from langchain.agents import create_agent

import base64

from langchain_core.messages import HumanMessage




#CREDENTIALS
USERNAME='admin'
PASSWORD='Developer@123'
cred = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()

headers = {
    "Content-Type": "application/json",
    "Accept-Encoding": "identity",  # disables compression for SSE
    "Authorization": f"Basic {cred}"

}

# Load openAI key from .env file
load_dotenv()
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0
)

async def main():
    custom_client = httpx.AsyncClient(verify=False, headers=headers)
    # Create MCP client with OpenSearch connection details
    client= MultiServerMCPClient(
    {
        "opensearch": { 
        "url": "http://localhost:9200/_plugins/_ml/mcp/sse?append_to_base_url=true",
        "transport": "sse",
         "headers": {
            "Content-Type": "application/json",
            "Accept-Encoding": "identity",  # Disable compression for SSE
        }
        }
    }
    )
    """
    direct_message = HumanMessage(
        content="Explain the difference between an SDK and an API in one sentence."
    )
    response = model.invoke([direct_message])
    print("\n--- Direct Model Response ---")
    print(response.content)
    """
    # Get available tools from the MCP server
    tools = await client.get_tools()
    #tools=["ListIndexTool", "SearchIndexTool"]
    # Initialize LangChain agent with tools and model
    agent = create_agent(
        model=model,
        tools=tools
    )

    # Execute agent with query to list products
    await agent.ainvoke({"input": "List all the products"})

if __name__ == "__main__":
    asyncio.run(main())