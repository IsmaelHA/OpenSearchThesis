from collections import defaultdict
import pandas
from statics import analize_results
from Knn.open_search_ingestion_pipeline import neural_search
from constants import MODEL_ID
from base_eval_model import Evaluator

class KnnEvaluator(Evaluator):
    def __init__(self, client):
        self.client = client

    def evaluate(self, eval_data,k):
        eval_logs(eval_data, self.client, k)

def eval_logs(log_data, client, k):
    """
    Perform a k-NN search to find logs similar to the given log_messages and process the response to give a predicted label
    """
    y_eval = log_data["label"]
    y_predict = []
    for row in log_data.itertuples():
        # Execute search
        similar_logs = neural_search(row.log_message, client,MODEL_ID,row.source, k)
        y_predict.append(process_response(similar_logs))
    analize_results(y_eval, y_predict,"Knn"+str(k))

def process_response(response):
    label_scores = defaultdict(float)

    # Sumar scores por label
    for item in response:
        label_scores[item["label"]] += item["score"]

    # Score total para normalizar
    total_score = sum(label_scores.values())

    # Normalizar a porcentaje
    label_percentages = {
        label: score / total_score * 100
        for label, score in label_scores.items()
    }
    # Devolver label más pesado
    most_likely = max(label_scores.items(), key=lambda x: x[1])
    #print(f"✅ Label más probable: {most_likely[0]} ({most_likely[1]:.2f} score)")
    
    return most_likely[0]
