# send_request_plain_async.py (with average time per alert)
import requests
import aiohttp # For asynchronous HTTP requests
import asyncio # For managing concurrent tasks
import time
import json
import argparse
import os
import traceback
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any, List

# --- Configuration ---
DEFAULT_VLLM_URL = "http://172.17.0.1:8000/v1/chat/completions" # Your vLLM endpoint
#DEFAULT_MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
DEFAULT_MODEL_NAME = "ZySec-AI/SecurityLLM"
#DEFAULT_MODEL_NAME = "Qwen/Qwen3-30B-A3B"
#DEFAULT_MODEL_NAME = "mistralai/Ministral-8B-Instruct-2410"
#DEFAULT_MODEL_NAME = "ministral/Ministral-3b-instruct"
DEFAULT_INPUT_ALERTS_PATH = "low_confidence_bfa_alerts.jsonl"
DEFAULT_OUTPUT_RESPONSES_PATH = "llm_responses_plain_async_benign.jsonl"
DEFAULT_SYSTEM_PROMPT_PATH = "system_prompt_plain.txt"
DEFAULT_MAX_CONCURRENT_REQUESTS = 200

# Define canonical labels
CanonicalLabel = Literal[
    "Benign", "DoS Attack", "DDoS Attack", "Port Scan",
    "Brute Force Attack", "Web Attack", "Botnet Attack",
    "Infiltration Attack", "Heartbleed",
]
# Define the enforced output schema
class LLMResponse(BaseModel):
    final_attack_label: CanonicalLabel
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)

def parse_args():
    parser = argparse.ArgumentParser(description="Send alerts to LLM (PLAIN - Async).")
    parser.add_argument("--llm_url", type=str, default=DEFAULT_VLLM_URL)
    parser.add_argument("--model_name", type=str, default=DEFAULT_MODEL_NAME)
    parser.add_argument("--alerts_file", type=str, default=DEFAULT_INPUT_ALERTS_PATH)
    parser.add_argument("--output_file", type=str, default=DEFAULT_OUTPUT_RESPONSES_PATH)
    parser.add_argument("--system_prompt_file", type=str, default=DEFAULT_SYSTEM_PROMPT_PATH)
    parser.add_argument("--max_concurrent_requests", type=int, default=DEFAULT_MAX_CONCURRENT_REQUESTS,
                        help="Maximum number of concurrent requests to the LLM.")
    return parser.parse_args()

def load_prompt(file_path: str) -> str:
    if not os.path.exists(file_path): print(f"ERROR: Prompt file not found: '{file_path}'"); exit()
    try:
        with open(file_path, "r", encoding='utf-8') as f: return f.read().strip()
    except Exception as e: print(f"Error reading prompt file '{file_path}': {e}"); exit()

async def process_single_alert(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    alert_index: int,
    original_alert: Dict,
    llm_url: str,
    model_name: str,
    system_prompt: str,
    json_schema: Dict
) -> Dict:
    """Processes a single alert by sending it to the LLM asynchronously."""
    async with semaphore:
        # print(f"--- Starting processing for Alert {alert_index + 1} ---") # Can be verbose
        request_start_time = time.monotonic() # Time for this specific request
        output_record = {"original_alert": original_alert, "status": "unknown_error", "error": "Unknown processing error"}
        try:
            alert_json_string = json.dumps(original_alert, indent=2)
            user_prompt_content = f"""Below, you find the details for an alert that requires re-evaluation:

Alert:
{alert_json_string}

Re-evaluate the alert based *only* on the provided alert details (predicted label, confidence, flow features, IPs, destination port). Assign a final label from the canonical list: {list(CanonicalLabel.__args__)}, provide a concise explanation, and indicate your confidence. Provide your response strictly following the agreed JSON output format."""

            payload = { "model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt_content}], "temperature": 0.7, "top_p": 0.9, "max_tokens": 1024, "guided_json": json_schema }

            async with session.post(llm_url, json=payload, timeout=120) as response:
                response_received_time = time.monotonic()
                elapsed_time_this_request = response_received_time - request_start_time
                # print(f"Alert {alert_index + 1}: LLM response received in {elapsed_time_this_request:.3f} seconds. Status: {response.status}")

                if response.ok:
                    result = await response.json()
                    if "choices" in result and len(result["choices"]) > 0 and "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                         llm_response_content_str = result["choices"][0]["message"]["content"].strip()
                    else:
                         print(f"ERROR (Alert {alert_index + 1}): Unexpected response format from LLM: {result}")
                         return {"original_alert": original_alert, "error": "Unexpected LLM response format", "status_code": response.status, "status": "format_error", "inference_time_sec": elapsed_time_this_request}

                    try:
                        llm_output_dict = json.loads(llm_response_content_str)
                        LLMResponse.model_validate(llm_output_dict)
                        output_record = {"original_alert": original_alert, "llm_response": llm_output_dict, "inference_time_sec": elapsed_time_this_request, "status": "success"}
                        # print(f"Alert {alert_index + 1}: Response parsed and validated successfully.")
                    except json.JSONDecodeError as json_err:
                        print(f"ERROR (Alert {alert_index + 1}): LLM response not valid JSON: {json_err}\nLLM Response: {llm_response_content_str}")
                        output_record = {"original_alert": original_alert, "error": f"JSONDecodeError: {json_err}", "raw_response": llm_response_content_str, "status": "json_error", "inference_time_sec": elapsed_time_this_request}
                    except Exception as val_err: # Pydantic validation error
                        print(f"ERROR (Alert {alert_index + 1}): LLM response validation failed: {val_err}\nLLM Response String: {llm_response_content_str}")
                        output_record = {"original_alert": original_alert, "error": f"ValidationError: {val_err}", "raw_response": llm_response_content_str, "status": "validation_error", "inference_time_sec": elapsed_time_this_request}
                else:
                    response_text = await response.text()
                    print(f"ERROR (Alert {alert_index + 1}): LLM API request failed. Status: {response.status}\nResponse: {response_text}")
                    output_record = {"original_alert": original_alert, "error": "LLM API request failed", "status_code": response.status, "response_text": response_text, "status": "api_error", "inference_time_sec": elapsed_time_this_request}
        except Exception as e:
            elapsed_time_this_request = time.monotonic() - request_start_time
            print(f"ERROR (Alert {alert_index + 1}): Failed processing. Error: {e}")
            traceback.print_exc()
            output_record = {"original_alert": original_alert, "error": str(e), "status": "processing_error", "inference_time_sec": elapsed_time_this_request}
        return output_record

async def main_async():
    args = parse_args()
    system_prompt = load_prompt(args.system_prompt_file)
    print(f"Loaded system prompt from {args.system_prompt_file}")
    try: json_schema = LLMResponse.model_json_schema(); print("Generated JSON schema for guided generation.")
    except Exception as e: print(f"Error generating Pydantic schema: {e}"); exit()
    if not os.path.exists(args.alerts_file): print(f"ERROR: Input alerts file not found: '{args.alerts_file}'"); exit()

    print(f"Processing alerts from: {args.alerts_file}"); print(f"Sending requests to: {args.llm_url}"); print(f"Saving plain responses to: {args.output_file}")

    all_alerts_data = []
    try:
        with open(args.alerts_file, 'r', encoding='utf-8') as f_in:
            for line_num, line in enumerate(f_in):
                try: all_alerts_data.append(json.loads(line.strip()))
                except json.JSONDecodeError: print(f"Warning: Skipping malformed JSON on line {line_num+1} in input file.")
    except Exception as e: print(f"ERROR reading input file: {e}"); exit()

    if not all_alerts_data: print("No valid alerts loaded from input file."); exit()
    num_alerts_to_process = len(all_alerts_data)
    print(f"Loaded {num_alerts_to_process} alerts to process.")

    # --- Start Overall Timer ---
    overall_start_time = time.monotonic()
    # ---

    semaphore = asyncio.Semaphore(args.max_concurrent_requests)
    tasks = []
    conn = aiohttp.TCPConnector(limit_per_host=args.max_concurrent_requests)
    async with aiohttp.ClientSession(connector=conn) as session:
        for i, alert_data in enumerate(all_alerts_data):
            task = process_single_alert(session, semaphore, i, alert_data, args.llm_url, args.model_name, system_prompt, json_schema)
            tasks.append(task)
        
        print(f"Launching {len(tasks)} processing tasks with max concurrency {args.max_concurrent_requests}...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # --- End Overall Timer ---
    overall_end_time = time.monotonic()
    total_processing_time = overall_end_time - overall_start_time
    # ---

    successful_responses = 0; failed_responses = 0
    with open(args.output_file, 'w', encoding='utf-8') as f_out:
        for result_item in results:
            if isinstance(result_item, Exception):
                print(f"ERROR: A task failed with an exception: {result_item}"); failed_responses +=1
            elif result_item and result_item.get("status") == "success":
                json.dump(result_item, f_out); f_out.write('\n'); successful_responses += 1
            elif result_item:
                json.dump(result_item, f_out); f_out.write('\n'); failed_responses += 1
            else: print(f"Warning: Empty or unexpected result item: {result_item}"); failed_responses += 1

    print("\n--- LLM Processing Summary ---")
    print(f"Total alerts attempted: {num_alerts_to_process}")
    print(f"Successful LLM responses saved: {successful_responses}")
    print(f"Failed LLM responses/errors: {failed_responses}")
    print(f"Output saved to: {args.output_file}")
    # --- Calculate and Print Time per Alert ---
    if num_alerts_to_process > 0:
        time_per_alert = total_processing_time / num_alerts_to_process
        print(f"Total processing time for all alerts: {total_processing_time:.2f} seconds")
        print(f"Average time per alert: {time_per_alert:.3f} seconds")
    # --- End Calculation ---
    print("--- Finished ---")

if __name__ == "__main__":
    asyncio.run(main_async())
