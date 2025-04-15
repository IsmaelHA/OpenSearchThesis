from ingest_pipeline import generate_embedding
from constants import *
from statics import *
def search_similar_logs(log_messages,client,model, k=5):
    """
    Perform a k-NN search to find logs similar to the given log_messages
    """

    for log_message in log_messages:
        # Execute search
        similar_logs = get_search_response(log_message,client,model,k)
        label_percent=analize_scores(similar_logs)
        save_results_to_file(label_percent, log_message)
        print(label_percent)
    # print("\nlog:", log, "\nSIMILAR LOGS =", similar_logs)

def get_search_response(log_message,client,model,k):
    query_vector = generate_embedding(log_message,model)

    # k-NN search query
    query = {
        "size": k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_vector,
                    "k": k
                }
            }
        }
    }
    response= client.search(index=INDEX_NAME, body=query)
    results = []
    # Extract results
    for hit in response["hits"]["hits"]:
        log_entry = {
            #"raw_message": hit["_source"]["embedding"],
            # Default to "No Label" if missing
            "label": hit["_source"].get("label", "No Label"),
            # Similarity score (optional, useful for ranking)
            "score": hit["_score"]
        }
        results.append(log_entry)
    return results