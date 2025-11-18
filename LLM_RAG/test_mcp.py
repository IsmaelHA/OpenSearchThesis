from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
import json
from langchain_core.messages import AIMessage
class Response(BaseModel):
    label: str
    explanation: str
SYSTEM_PROMPT = (
    "You are a log-based Intrusion Detection System (IDS). "
    # "The network includes this services: a web server, cloud file share, mail servers, VPN gateway, DNS, internal intranet, a firewall, four internal employees, three remote employees, and three external users. "
    # f"Assign a label from the label list: {list(LabelList.__args__)} based on the content "
    "Your response must strictly follow the JSON format defined in the schema provided. "
    "Only return valid labels allowed by the schema."
    "You will be provided with:\n"
    "1. A list of similar past logs with known labels and the similarity score.\n"
    "2. A new log message with the source to classify.\n"
    "Use the context logs to inform your prediction. If the new log is similar to known attack patterns, label it accordingly. "
    "In addition to the label, provide a short explanation (in plain English, max 70 words) describing the reasoning behind your decision. Let me know if your decision is based on the provided list of logs or not."
)
JSON_SCHEMA=Response.model_json_schema()
SYSTEM_PROMPT = (
    "You are a log-based Intrusion Detection System (IDS). "
    "Assign a label to the log "
    "Your response must strictly follow the JSON format defined in the schema provided. "
    "Only return valid labels allowed by the schema."
    "You will be provided with:\n"
    "1. A list of similar past logs with known labels and the similarity score.\n"
    "2. you can call tools to get context.\n"
    "Use the context logs to inform your prediction. If the new log is similar to known attack patterns, label it accordingly. "
    "In addition to the label, provide a short explanation (in plain English, max 40 words) describing the reasoning behind your decision. Let me know if your decision is based on the provided list of logs or not."
)
response=Response(label="labe",explanation="e")

async def main():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",  # HTTP-based remote server
                # Ensure you start your weather server on port 8000
                "url": "http://localhost:8000/mcp",
            }
        }
    )
    # Load openAI key from .env file
    load_dotenv()
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0
    )
    tools = await client.get_tools()
    agent = create_agent(
        model=model,
        tools=tools
    )

    agent_response = await agent.ainvoke(
        {"messages": [{"role": "system",
                       "content": SYSTEM_PROMPT}, {"role": "user", "content": "label the log \"Database migration started.\" from db_connector. use the RAG , use less than 50 words"}],
         "temperature": 0.3,  # Adjust for creativity vs. determinism
         "max_tokens": 150,    # Adjust based on expected response length
         "stream": False,
         "guided_json": JSON_SCHEMA}
    )
    print(agent_response)
    final_output = extract_last_ai_message(agent_response)
    response=Response(label=final_output["messages"][0]["label"],explanation=final_output["messages"][0]["explanation"])
    print("LABEL: ",response.label)
    print("EXPLANATION: ",response.explanation)


def extract_last_ai_message(response_data):
    """
    Captures the content of the last AIMessage in the list,
    extracts the JSON content, and returns the formatted response.
    """
    messages = response_data.get('messages', [])
    
    # 1. Identify the last message
    last_message = messages[-1] if messages else None

    # 2. Check if the last message is an AIMessage (Final response)
    if isinstance(last_message, AIMessage):
        raw_content = last_message.content
        
        # 3. Extract and clean the JSON string
        # The content is wrapped in ```json\n...\n```
        try:
            # Simple string cleaning to extract the JSON block
            json_string = raw_content.strip().replace('```json\n', '').replace('\n```', '').strip()
            
            # 4. Load the JSON string into a Python dictionary
            parsed_json = json.loads(json_string)
            
            # 5. Return the desired dictionary structure
            return {
                'messages': [parsed_json]
            }
        
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing JSON from AI content: {e}")
            return {'messages': [{'error': 'Could not parse final AI response.'}]}
    
    else:
        # Handle cases where the final message might be a ToolMessage or AIMessage with tool_calls
        return {'messages': [{'error': 'Last message was not a final AI response.'}]}



if __name__ == "__main__":
    asyncio.run(main())
