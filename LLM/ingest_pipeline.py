import requests
import json
from pydantic import BaseModel
from typing import Literal
# Data model for LLM to generate
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
LLM_URL = "http://155.54.95.92:8000/v1/chat/completions"


class Response(BaseModel):
    label: Literal["normal_log", "dnsteal","attacker_http","service_scan","dns_scan","network_scan","escalate","attacker_vpn","webshell_cmd","dirb","escalated_command","wpscan","traceroute","attacker_change_user" ]
    explanation: str
# --- Configuration ---
# LLM endpoint URL, updated to the user-provided IP and port

# --- Sample Prompt ---
# You can change this to any prompt you want to send
#SYSTEM_PROMPT = "You are going to act as a Intrusion Detection System, labeling the logs and explaining the attacksin 50 words.The log is between \"\n"
JSON_SCHEMA=Response.model_json_schema()
SYSTEM_PROMPT = (
    "You are a log-based Intrusion Detection System (IDS). "
    "The network includes this services: a web server, cloud file share, mail servers, VPN gateway, DNS, internal intranet, a firewall, four internal employees, three remote employees, and three external users. "
    "Your task is to analyze one log message and assign it an appropriate label based on its content. "
    "In addition to the label, provide a short explanation (in plain English, max 50 words) describing the reasoning behind your decision. "
    "Your response must strictly follow the JSON format defined in the schema provided. "
    "Only return valid labels allowed by the schema. The log message is shown below:"
)
def get_label( log_message: str,source:str):
    """
    Sends a prompt to the LLM and prints the response.
    """
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system",
             "content": SYSTEM_PROMPT},
            {"role": "user",
            "content": f" source: {source} ,log message: \"{log_message}\""}
        ],
        "temperature": 0.3,  # Adjust for creativity vs. determinism
        "max_tokens": 150,    # Adjust based on expected response length
        "stream": False,
        "guided_json": JSON_SCHEMA
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