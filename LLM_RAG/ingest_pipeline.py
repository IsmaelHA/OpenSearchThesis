import requests
import json
from pydantic import BaseModel

# Data model for LLM to generate
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
LLM_URL = "http://155.54.95.92:8000/v1/chat/completions"


class Response(BaseModel):
    label: str
    explanation: str
# --- Configuration ---
# LLM endpoint URL, updated to the user-provided IP and port
# --- Sample Prompt ---
# You can change this to any prompt you want to send
SYSTEM_PROMPT = "You are going to act as a Intrusion Detection System, labeling the logs (normal_log or attack) and explaining the attacks in 50 words.The log is between \"\n"


def get_label( log_message: str,source : str, rag:str):
    """
    Sends a prompt to the LLM and prints the response.
    """
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system",
             "content": SYSTEM_PROMPT+ f"Here you have a RAG with the most similar labeled logs: {rag}"
             + f" The JSON object must use the schema: {json.dumps(Response.model_json_schema(), indent=1)}"},
            {"role": "user",
            "content": f"Source: {source}, log message: \"{log_message}\""}
        ],
        "temperature": 0.3,  # Adjust for creativity vs. determinism
        "max_tokens": 150,    # Adjust based on expected response length
        # "guided_json" and other specific parameters from the original script
        # are removed for simplicity, as they require more setup (e.g., Pydantic schemas).
        # If the server requires a specific output structure (like JSON),
        # you might need to add "guided_json" back or adjust the prompt accordingly.
        "stream": False,
        # Enable JSON mode by setting the response format
        "response_format": {"type": "json_object"},
    }

    # print(f"Sending request to: {llm_url}")
    # print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        # Send the POST request
        response = requests.post(
            LLM_URL, json=payload, timeout=60)  # Added a timeout

        # print(f"\n--- LLM Response ---")
        # Check if the request was successful
        if response.ok:

            result = response.json()
            # print(result["choices"][0]["message"]["content"])
            try:
                return Response.model_validate_json(result["choices"][0]["message"]["content"])
            except Exception as e:
                print("An Error occurs validating the JSON:")
                print(type(e).__name__, "-", str(e))
                return None
        else:
            print(f"ERROR: LLM API request failed.")
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request to LLM failed: {e}")
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not decode JSON response: {e}")
        if 'response' in locals():  # Check if response variable exists
            print(f"Raw response text: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def print_response(response: Response):
    print("Label:", response.label)
    print("\nExplanation:",response.explanation)


#log="Jan 21 00:00:09 dnsmasq[3468]: query[A] 3x6-.596-.IunWTzebVlyAhhHj*ZfWjOBun1zAf*Wgpq-.YarqcF7oovex5JXZQp35nThgDU1Q3p3lT/-.DM6Vx/vcq3AkrO4Xh2kjojk8RCiDE2wjSv-.gY6ONv8eNmDck8gGwJ8fU3PPctbthfeDZT-.customers_2017.xlsx.email-19.kennedy-mendoza.info from 10.143.0.103"
#response= get_label(log)
#print_response(response)