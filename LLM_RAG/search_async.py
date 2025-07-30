# send_request_plain_async.py (with average time per alert)
import requests
import aiohttp # For asynchronous HTTP requests
import asyncio # For managing concurrent tasks
import time
import json
import pandas as pd
import traceback
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any, List
from statics import analize_results
from base_eval_model import Evaluator
from Knn.open_search_ingestion_pipeline import neural_search, create_action, send_actions
from constants import MODEL_ID
class LlmRagEvaluator(Evaluator):
    def __init__(self, open_search_client):
        self.open_search_client = open_search_client

    def evaluate(self, eval_data,k):
        asyncio.run(main_async(eval_data,self.open_search_client, k))

# --- Configuration ---
LabelList = Literal["normal_log", "dnsteal","attacker_http","service_scan","dns_scan","network_scan","escalate","attacker_vpn","webshell_cmd","dirb","escalated_command","wpscan","traceroute","attacker_change_user" ]

class Response(BaseModel):
    label: str
    explanation: str
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
LLM_URL = "http://155.54.95.92:8000/v1/chat/completions"
JSON_SCHEMA=Response.model_json_schema()
SYSTEM_PROMPT = (
    "You are a log-based Intrusion Detection System (IDS). "
    "The network includes this services: a web server, cloud file share, mail servers, VPN gateway, DNS, internal intranet, a firewall, four internal employees, three remote employees, and three external users. "
    f"Assign a label from the label list: {list(LabelList.__args__)} based on the content "
    "Your response must strictly follow the JSON format defined in the schema provided. "
    "Only return valid labels allowed by the schema."
    "You will be provided with:\n"
    "1. A list of similar past logs with known labels and the similarity score.\n"
    "2. A new log message with the source to classify.\n"
    "Use the context logs to inform your prediction. If the new log is similar to known attack patterns, label it accordingly. "
    "In addition to the label, provide a short explanation (in plain English, max 70 words) describing the reasoning behind your decision. Let me know if your decision is based on the provided list of logs or not."
)
DEFAULT_INPUT_ALERTS_PATH = "low_confidence_bfa_alerts.jsonl"
DEFAULT_OUTPUT_RESPONSES_PATH = "llm_responses_plain_async_benign.jsonl"
DEFAULT_SYSTEM_PROMPT_PATH = "system_prompt_plain.txt"
DEFAULT_MAX_CONCURRENT_REQUESTS = 400

def process_respose(response:Response,log_f,log_message:str,source:str,client):
    if "normal" not in response.label:
        #write the alert in a file
        log_f.write(f"Log query: {log_message}\n")
        log_f.write(f"Label: {response.label}\n")
        log_f.write(f"Explanation: {response.explanation}\n")
        log_f.write("#" * 80 + "\n")  # Separator for readability
    #add_rag(log_message,source, response.label, client)
    
async def process_single_alert(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    log_index: int,
    log_message: str,
    source:str,
    open_search_client,label:str,
    k
) -> Dict:
    """Processes a single alert by sending it to the LLM asynchronously."""
    
    async with semaphore:
        rag = get_rag(log_message,source, open_search_client,k)
        user_input = f"""Context logs:
            {rag}\n
            Classify:
            source: {source} ,log message: \"{log_message}\"
            """
        # print(f"--- Starting processing for Alert {alert_index + 1} ---") # Can be verbose
        request_start_time = time.monotonic() # Time for this specific request
        try:
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system",
                    "content": SYSTEM_PROMPT},
                    {"role": "user",
                    "content": f"{user_input}"}
                ],
                "temperature": 0.3,  # Adjust for creativity vs. determinism
                "max_tokens": 150,    # Adjust based on expected response length
                "stream": False,
                "guided_json": JSON_SCHEMA
            }

            async with session.post(LLM_URL, json=payload, timeout=1200) as response:
                #response_received_time = time.monotonic()
                #elapsed_time_this_request = response_received_time - request_start_time
                #print(f"Alert {log_index + 1}: LLM response received in {elapsed_time_this_request:.3f} seconds. Status: {response.status}")
                
                if response.ok:
                    result = await response.json()
                    try:
                        return {
                            "index": log_index,
                            "log_message": log_message,
                            "source": source, # It's good to return source too if it's part of your context
                            "llm_response": Response.model_validate_json(result["choices"][0]["message"]["content"]),
                            "true_label" : label
                        }
                    except Exception as e:
                        print("An Error occurs validating the JSON:")
                        print(type(e).__name__, "-", str(e))
                        return Exception
                else:
                    response_text = await response.text()
                    print(f"ERROR (Alert {log_index + 1}): LLM API request failed. Status: {response.status}\nResponse: {response_text}")
        except Exception as e:
            elapsed_time_this_request = time.monotonic() - request_start_time
            print(f"ERROR (Alert {log_index + 1}): Failed processing. Error: {e}")
            traceback.print_exc()
        return Exception

async def main_async(eval_df,open_search_client, k):
    # --- Start Overall Timer ---
    overall_start_time = time.monotonic()
    y_true=[]
    y_predict=[]
    semaphore = asyncio.Semaphore(DEFAULT_MAX_CONCURRENT_REQUESTS)
    tasks = []
    conn = aiohttp.TCPConnector(limit_per_host=DEFAULT_MAX_CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(connector=conn) as session:
        for i, (index, row) in enumerate(eval_df.iterrows()):
            #print(row)
            task = process_single_alert(session, semaphore, i, row.log_message, row.source,open_search_client,row.label,k)
            tasks.append(task)
        
        print(f"Launching {len(tasks)} processing tasks with max concurrency {DEFAULT_MAX_CONCURRENT_REQUESTS}...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # --- End Overall Timer ---
    overall_end_time = time.monotonic()
    total_processing_time = overall_end_time - overall_start_time
    # ---

    successful_responses = 0; failed_responses = 0
    with open("llm_attack_explanations", 'w', encoding='utf-8') as f_out:
        for result_item in results:
            if isinstance(result_item, Exception):
                print(f"ERROR: A task failed with an exception: {result_item}"); failed_responses +=1
            else: 
                try:
                    if isinstance(result_item.get("llm_response"),Response):
                        response=result_item.get("llm_response")
                        process_respose(response,f_out,result_item.get("log_message"),result_item.get("log_message"),open_search_client)
                        y_predict.append(response.label)
                        y_true.append(result_item.get("true_label"))
                        successful_responses += 1
                except Exception as e:
                        print("An Error occurs validating the Respose:")
                        print(type(e).__name__, "-", str(e))
                        print(f"Warning: Empty or unexpected result item: {result_item}"); failed_responses += 1
    
    analize_results(y_true,y_predict,evaluator="Llm_rag")
    print("\n--- LLM Processing Summary ---")
    #print(f"Total alerts attempted: {num_alerts_to_process}")
    print(f"Successful LLM responses saved: {successful_responses}")
    print(f"Failed LLM responses/errors: {failed_responses}")
    #print(f"Output saved to: {args.output_file}")
    # --- Calculate and Print Time per Alert ---
    """
    if num_alerts_to_process > 0:
        time_per_alert = total_processing_time / num_alerts_to_process
        print(f"Total processing time for all alerts: {total_processing_time:.2f} seconds")
        print(f"Average time per alert: {time_per_alert:.3f} seconds")
    # --- End Calculation ---"""
    print("--- Finished ---")

def add_rag(log_message,source, label, client):
    actions = []
    actions.append(create_action(log_message,source, label))
    send_actions(client, actions)

def get_rag(log_message,source, client,k):
    return neural_search(log_message, client, MODEL_ID, source,k)