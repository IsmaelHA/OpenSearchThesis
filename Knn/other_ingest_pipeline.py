from sentence_transformers import SentenceTransformer
from opensearchpy import helpers
import os
import json
import pandas as pd


"""def ingest_logs(gather_dir,client,model):
    actions = []
    # Walk through the gather directory recursively
    for root, dirs, files in os.walk(gather_dir):
        print("---Files:", files)
        for file in files:
            if ".log" in file:
                file_path = os.path.join(root, file)
                if "attacker" in file_path:
                    continue
                if "logs" not in file_path:
                    continue
                # check if there is a file with labels or not
                labels = get_labels(file_path)

                label = "Normal Log"
                print("file path inside", file_path)
                with open(file_path, 'r', encoding='utf-8') as log_f:
                    i=0
                    for line_number, line in enumerate(log_f, 1):
                        line = line.strip()
                        
                        if not line:
                            continue
                        if line_number > LOGS_PER_FILE:
                            break
                        # Generate embedding for the raw log line
                        embedding = generate_embedding(line,model)

                        label = get_label(labels, line_number)
                        doc = {
                            "embedding": embedding,
                            "label": label
                        }
                        action = {
                            "_index": INDEX_NAME,
                            "_source": doc
                        }
                        actions.append(action)
                        i=i+1
                        if i>10:
                            helpers.bulk(client, actions)
                            actions = []
                            i=0
                if actions:
                    helpers.bulk(client, actions)
                    print(f"Ingested {len(actions)} documents into '{INDEX_NAME}' index.")
                else:
                    print("No log documents found to ingest.")"""


def ingest_from_csv(data, client, model):
    actions = []
    # Walk through the gather directory recursively
    i = 0
    print(data.head())
    for row in data.itertuples(index=False):
        log_message = row.log_message
        label = row.label
        # Generate embedding for the raw log line
        embedding = generate_embedding(log_message, model)
        doc = {
            "log": log_message,
            "embedding": embedding,
            "label": label
        }
        action = {
            "_index": INDEX_NAME,
            "_source": doc
        }
        actions.append(action)
        i = i+1
        if i > 10:
            helpers.bulk(client, actions)
            actions = []
            i = 0
        if actions:
            helpers.bulk(client, actions)
            print(
                f"Ingested {len(actions)} documents into '{INDEX_NAME}' index.")
        else:
            print("No log documents found to ingest.")


def ingest_from_csv_batches(data, client, model, batch_size=32):
    actions = []
    batch_logs = []
    batch_labels = []

    for idx, row in enumerate(data.itertuples(index=False)):
        batch_logs.append(row.log_message)
        batch_labels.append(row.label)

        # When batch is full or at the end of the dataset
        if len(batch_logs) == batch_size or idx == len(data) - 1:
            # Batch encode
            # or True if you want torch tensors
            embeddings = model.encode(batch_logs, convert_to_tensor=False)
            # Build actions
            for log_message, label, embedding in zip(batch_logs, batch_labels, embeddings):
                doc = {
                    "log": log_message,
                    "embedding": embedding.tolist(),
                    "label": label
                }
                action = {
                    "_index": INDEX_NAME,
                    "_source": doc
                }
                actions.append(action)

            # Bulk insert
            if actions:
                helpers.bulk(client, actions)
                print(
                    f"Ingested {len(actions)} documents into '{INDEX_NAME}' index.")

            # Reset batches
            actions = []
            batch_logs = []
            batch_labels = []


def ingest_from_csv_batches_pipeline(data, client, model, batch_size=32):
    actions = []
    batch_logs = []
    batch_labels = []

    for idx, row in enumerate(data.itertuples(index=False)):
        batch_logs.append(row.log_message)
        batch_labels.append(row.label)

        # When batch is full or at the end of the dataset
        if len(batch_logs) == batch_size or idx == len(data) - 1:
            # Build actions
            for log_message, label in zip(batch_logs, batch_labels):
                doc = {
                    "log": log_message,
                    "label": label
                }
                action = {
                    "_index": INDEX_NAME,
                    "_source": doc
                }
                actions.append(action)

            # Bulk insert
            if actions:
                helpers.bulk(client, actions)
                print(
                    f"Ingested {len(actions)} documents into '{INDEX_NAME}' index.")

            # Reset batches
            actions = []
            batch_logs = []
            batch_labels = []
