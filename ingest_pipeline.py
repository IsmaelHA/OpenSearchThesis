import os
import json
from constants import *
from opensearchpy import helpers
def create_index(client):
    # Create the index with mapping for raw_message and embedding vector
    mapping = {
        "settings": {
            "index.knn": "true"
        },
        "mappings": {
            "properties": {
                "embedding": {
                    "type": "knn_vector",
                            "dimension": VECTOR_SIZE,
                            "space_type": "l2",
                    "data_type": "float",
                    "mode": "on_disk",
                    "compression_level": "32x",
                    "method": {
                        "name": "hnsw",
                        "engine": "faiss",
                                  "parameters": {
                                      "ef_construction": 64,
                                      "m": 16
                                  }
                    }
                },  # for all-MiniLM-L6-v2, the dimension is 384
                "label": {"type": "text"}
            }
        }
    }
    if not client.indices.exists(INDEX_NAME):
        client.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Index '{INDEX_NAME}' created.")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")


def generate_embedding(message,model):
    # Generate an embedding vector for the provided message
    vector = model.encode(message).tolist()
    if len(vector) < VECTOR_SIZE:
        vector.extend([0] * (VECTOR_SIZE - len(vector)))
    elif len(vector) > VECTOR_SIZE:
        vector = vector[:2048]
    return vector


def read_labels(file_path):
    """
    Reads a log file and creates a dictionary mapping line numbers to labels.
    """
    line_to_labels = {}

    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
            if line_number > LOGS_PER_FILE:
                break
            line = line.strip()
            if not line:
                continue
            print("READING THE JSON")
            try:
                log_entry = json.loads(line)  # Parse JSON
                line_number = log_entry.get("line")
                #print("line_number", line_number)
                labels = log_entry.get("labels", [])
                label = labels[0]
                #print("label", labels)
                if line_number is not None:
                    line_to_labels[line_number] = label  # Store in dictionary
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line in {file_path}: {line}")

    return line_to_labels


def get_labels(file_path):
    # Change the file file_path
    # Substitute the gather word to the label word in the file_path variable
    file_path = file_path.replace("gather", "labels")
    # Get the label from the file file_path
    if (not (os.path.isfile(file_path))):
        return None
    else:
        return read_labels(file_path)


def get_label(labels, line_number):
    if labels == None:
        return "normal_log"
    elif ((label := labels.get(line_number)) == None):
        return "normal_log"
    else:
        return label
def ingest_logs(gather_dir,client,model):
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
                    print("No log documents found to ingest.")
"""def send_no_labeled_logs(file_path):
    label = "Normal Log"
    with open(file_path, 'r', encoding='utf-8') as log_f:
        for line_number, line in enumerate(log_f, 1):
            line = line.strip()
            actions = []
            if not line:
                continue
            if line_number > 100:
                break
            # Generate embedding for the raw log line
            embedding = generate_embedding(line)

            doc = {
                "raw_message": line,
                "embedding": embedding,
                "label": label
            }
            action = {
                "_index": INDEX_NAME,
                "_source": doc
            }
            actions.append(action)
            helpers.bulk(client, actions)


def send_labeled_logs(file_path):
    label = "Normal Log"
    with open(file_path, 'r', encoding='utf-8') as log_f, open(label_path, "r", encoding="utf-8") as label_file:
        for line_number, line in enumerate(log_f, 1):
            line = line.strip()
            actions = []
            if not line:
                continue
            if line_number > 100:
                break
            # Generate embedding for the raw log line
            embedding = generate_embedding(line)

            doc = {
                "raw_message": line,
                "embedding": embedding,
                "label": label
            }
            action = {
                "_index": INDEX_NAME,
                "_source": doc
            }
            actions.append(action)
            helpers.bulk(client, actions)

"""