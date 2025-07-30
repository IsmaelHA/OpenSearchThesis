from Knn.open_search_ingestion_pipeline import neural_search, create_action, send_actions
from LLM_RAG.ingest_pipeline import *
from statics import analize_results
from base_eval_model import Evaluator
from constants import ATTACKS_LOG_FILE, MODEL_ID


class LlmRagEvaluator(Evaluator):
    def __init__(self, llm_client, open_search_client):
        self.llm_client = llm_client
        self.open_search_client = open_search_client

    def evaluate(self, eval_data):
        eval_logs(eval_data, self.llm_client, self.open_search_client, k=5)


def eval_logs(log_data, open_search_client):
    y_eval = log_data["label"]
    y_predict = []
    with open(ATTACKS_LOG_FILE, "a", encoding="utf-8") as log_f:
        for row in log_data.itertuples():
            # Execute search
            rag = get_rag(row.log_message,row.source, open_search_client,MODEL_ID)
            response = get_label(row.log_messag,row.source, rag)
            y_predict.append(process_respose(
                response, log_f, row.log_message, row.source, open_search_client))
    analize_results(y_eval, y_predict,"Llm_rag")


def process_respose(response: Response, log_f, log_message: str,source, open_search_client):
    if "normal" not in response.label:
        # write the alert in a file
        log_f.write(f"Log query: {log_message}\n")
        log_f.write(f"Label: {response.label}\n")
        log_f.write(f"Explanation: {response.explanation}\n")
        log_f.write("#" * 80 + "\n")  # Separator for readability
        label = "attack_log"
    else:
        label = "normal_log"
    add_rag(log_message, source, label, open_search_client)






