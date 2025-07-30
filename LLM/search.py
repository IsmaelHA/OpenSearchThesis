from LLM.ingest_pipeline import get_label, Response
from statics import analize_results
from constants import ATTACKS_LOG_FILE
from base_eval_model import Evaluator



def eval_logs(log_data):
    y_eval= log_data["label"]
    y_predict=[]
    with open(ATTACKS_LOG_FILE, "a", encoding="utf-8") as log_f:
        for row in log_data.itertuples():
            response = get_label(row.log_message, row.source)
            if response:
                y_predict.append(process_respose(response,log_f,row.log_message))
            else:
                del y_eval[len(y_predict)]
    analize_results(y_eval,y_predict,evaluator="Llm")
        
def process_respose(response:Response,log_f,log_message: str):
    if "normal" not in response.label:
        #write the alert in a file
        log_f.write(f"Log query: {log_message}\n")
        log_f.write(f"Label: {response.label}\n")
        log_f.write(f"Explanation: {response.explanation}\n")
        log_f.write("#" * 80 + "\n")  # Separator for readability
        return "attack_log"
    else:
        return "normal_log"


