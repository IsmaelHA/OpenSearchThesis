from constants import *
from opensearchpy import helpers


def create_index(client):
    # Create the index with mapping for raw_message and embedding vector
    mapping = {
        "settings": {
            "index.knn": "true",
            "default_pipeline": "log-filter-pipeline"

        },
        "mappings": {
            "properties": {
                "log": {"type": "text"},
                "embedding": {
                    "type": "knn_vector",
                            "dimension": VECTOR_SIZE,
                    "data_type": "float",
                    "mode": "on_disk",
                    "compression_level": "32x",
                    "method": {
                        "name": "hnsw",
                        "engine": "faiss",
                        "space_type": "cosinesimil",
                                  "parameters": {
                                      "ef_construction": 64,
                                      "m": 35
                                  }
                    }
                },  # for all-MiniLM-L6-v2, the dimension is 384
                "source": {"type": "text"},
                "label": {"type": "text"}
            }
        }
    }
    if not client.indices.exists(INDEX_NAME):
        client.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Index '{INDEX_NAME}' created.")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")


def generate_embedding(message, model):
    # Generate an embedding vector for the provided message
    vector = model.encode(message).tolist()
    """if len(vector) < VECTOR_SIZE:
        vector.extend([0] * (VECTOR_SIZE - len(vector)))
    elif len(vector) > VECTOR_SIZE:
        vector = vector[:VECTOR_SIZE]"""
    return vector


def neural_search(log_message, client, model_id, source, k):

    if source == None:
        query = {
            "_source": {
                "excludes": [
                    "embedding"
                ]
            },
            "size": 2,
            "query": {
                "neural": {
                    "embedding": {
                        "query_text": f"{log_message}",
                        "model_id": f"{model_id}",
                        "k": k,
                    }
                }
            }
        }
    else:
        query = {
            "_source": {
                "excludes": [
                    "embedding"
                ]
            },
            "size": 2,
            "query": {
                "neural": {
                    "embedding": {
                        "query_text": f"{log_message}",
                        "model_id": f"{model_id}",
                        "k": k,
                        "filter": {
                            "bool": {
                                "must": [
                                    {
                                        "term": {
                                            "source": f"{source}"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    response = client.search(index=INDEX_NAME, body=query)
    results = []
    # Extract results

    for hit in response["hits"]["hits"]:
        log_entry = {
            # "raw_message": hit["_source"]["embedding"],
            # Default to "No Label" if missing
            "log": hit["_source"].get("log"),
            "label": hit["_source"].get("label", "No Label"),
            # Similarity score (optional, useful for ranking)
            "score": hit["_score"]
        }
        results.append(log_entry)
    if not results:
        print("SOURCE", source, "LEN", len(source))

        if '-' in source:
            source = source.split('-')
            source = source[1]
        elif "_" in source:
            source = source.split('_')
            source = source[1]
        else:
            source = None
        results = neural_search(log_message, client, MODEL_ID, source, k=k)
    return results


def ingest_batches_from_csv_pipeline(data, client, batch_size=64):
    actions = []
    batch_logs = []
    batch_labels = []
    batch_sources = []
    for idx, row in enumerate(data.itertuples(index=False)):
        batch_logs.append(row.log_message)
        batch_sources.append(row.source)
        batch_labels.append(row.label)

        # When batch is full or at the end of the dataset
        if len(batch_logs) == batch_size or idx == len(data) - 1:
            # Build actions
            for log_message, source, label in zip(batch_logs, batch_sources, batch_labels):
                actions.append(create_action(log_message, source, label))

            # Bulk insert
            if actions:
                send_actions(client, actions)
                print(
                    f"Ingested {len(actions)} documents into '{INDEX_NAME}' index.")

            # Reset batches
            actions = []
            batch_logs = []
            batch_labels = []


def create_action(log_message, source, label):
    doc = {
        "log": log_message,
        "source": source,
        "label": label
    }
    return {
        "_index": INDEX_NAME,
        "_source": doc
    }


def send_actions(client, actions):
    helpers.bulk(client, actions)
