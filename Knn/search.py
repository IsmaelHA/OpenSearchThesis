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

    """print("Porcentajes por label:")
    for label, percentage in label_percentages.items():
        print(f"  {label}: {percentage:.2f}%")

    # Aviso 1: normal_log no es mayor que el resto juntos
    normal_score = label_scores.get("normal_log", 0)
    others_score = total_score - normal_score

    if normal_score <= others_score:
        print("⚠️  Alerta: 'normal_log' no domina. El resto tiene más score total.")
    
    # Aviso 2: hay otros labels distintos a 'normal_log'
    if any(label != "normal_log" for label in label_scores):
        print("⚠️  Alerta: Se han detectado logs no normales (potenciales ataques).")
    """
    # Devolver label más pesado
    most_likely = max(label_scores.items(), key=lambda x: x[1])
    #print(f"✅ Label más probable: {most_likely[0]} ({most_likely[1]:.2f} score)")
    
    return most_likely[0]
