import os
import re
import json
from datetime import datetime
from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer

# Initialize OpenSearch client
client = OpenSearch(hosts=[{'host': 'localhost', 'port': 9200}], http_auth=('admin', 'Developer@123'), use_ssl=True,
                    verify_certs=False)

INDEX_NAME = "labeled-logs"
DIRECTORY = "C:\\Users\\elcrio\\Desktop\\TFG\\"
VECTOR_SIZE = 2048
# You can change this to a cybersecurity-specific model if available
model = SentenceTransformer('all-MiniLM-L6-v2')


def create_index():
    # Create the index with mapping for raw_message and embedding vector
    mapping = {
        "settings": {
            "index.knn": "true"
        },
        "mappings": {
            "properties": {
                "raw_message": {"type": "text"},
                "embedding": {"type": "knn_vector",
                              "dimension": VECTOR_SIZE,
                              "space_type": "l2",
                              "mode": "on_disk",
                              "method": {
                                  "name": "hnsw"
                              }},  # for all-MiniLM-L6-v2, the dimension is 384
                "label": {"type": "text"}
            }
        }
    }
    if not client.indices.exists(INDEX_NAME):
        client.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Index '{INDEX_NAME}' created.")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")


def generate_embedding(message):
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
        for line_number,line in enumerate(file,1):
            if line_number > 100:
                break
            line = line.strip()
            if not line:
                continue
            print("READING THE JSON")
            try:
                log_entry = json.loads(line)  # Parse JSON
                line_number = log_entry.get("line")
                print("line_number",line_number)
                labels = log_entry.get("labels", [])
                print("label",labels)
                if line_number is not None:
                    line_to_labels[line_number] = labels  # Store in dictionary
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line in {file_path}: {line}")

    return line_to_labels


def get_labels(file_path):
    file_path=DIRECTORY+"gather\\inet-firewall\\logs\\dnsmasq.log"
    #file_path= "JOSEMI"
    # Change the file file_path
    # Substitute the gather word to the label word in the file_path variable
    file_path = file_path.replace("gather", "labels")
    # Get the label from the file file_path
    print(file_path)
    if (not (os.path.isfile(file_path))):
        return None
    else:
       return read_labels(file_path)

def get_label(labels,line_number):
    if labels==None:
        return "Normal Log"
    elif ((label:=labels.get(line_number))==None):
        return "Normal Log"
    else:
        return label


def open_file(file_path):
    file_path = file_path.replace("gather", "labels")
    return os.path.isfile(file_path)


def ingest_logs(gather_dir):
    actions = []
    # Walk through the gather directory recursively
    for root, dirs, files in os.walk(gather_dir):
        print("---Files:", files)
        for file in files:
            # If there is label file call a function if not call another
            if open_file(file):
                print("File exists")
            else:
                print("File does not exist")
            if file.endswith('.log'):
                file_path = os.path.join(root, file)
                #check if there is a file with labels or not
                labels=get_labels(file_path)
                
                label= "Normal Log"
                print("file path inside",file_path)
                with open(file_path, 'r', encoding='utf-8') as log_f:
                    for line_number, line in enumerate(log_f, 1):
                        line = line.strip()
                        actions=[]
                        if not line:
                            continue
                        if line_number >100:
                            break
                        # Generate embedding for the raw log line
                        embedding = generate_embedding(line)
                        
                        label = get_label(labels,line_number)
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
                        helpers.bulk(client,actions)
    if actions:
        #helpers.bulk(client, actions)
        print(f"Ingested {len(actions)} documents into '{INDEX_NAME}' index.")
    else:
        print("No log documents found to ingest.")

def send_no_labeled_logs(file_path):
    label= "Normal Log"
    with open(file_path, 'r', encoding='utf-8') as log_f:
        for line_number, line in enumerate(log_f, 1):
            line = line.strip()
            actions=[]
            if not line:
                continue
            if line_number >100:
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
            helpers.bulk(client,actions)

def send_labeled_logs(file_path):
    label= "Normal Log"
    with open(file_path, 'r', encoding='utf-8') as log_f,open(label_path, "r", encoding="utf-8") as label_file:
        for line_number, line in enumerate(log_f, 1):
            line = line.strip()
            actions=[]
            if not line:
                continue
            if line_number >100:
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
            helpers.bulk(client,actions)
def search_similar_logs(log_message, k=5):
    """
    Perform a k-NN search to find logs similar to the given log_message.

    :param log_message: The raw log message to search for similar logs.
    :param k: The number of nearest neighbors to retrieve.
    :param num_candidates: The number of candidates to consider for nearest neighbor search.
    :return: List of similar log messages.
    """
    # Generate embedding for the input log message
    query_vector = generate_embedding(log_message)

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

    # Execute search
    response = client.search(index=INDEX_NAME, body=query)
    results=[]
    # Extract results
    for hit in response["hits"]["hits"]:
        log_entry = {
            "raw_message": hit["_source"]["raw_message"],
            "label": hit["_source"].get("label", "No Label"),  # Default to "No Label" if missing
            "score": hit["_score"]  # Similarity score (optional, useful for ranking)
        }
        results.append(log_entry)
    return results

def save_results_to_file(results, log_query,filename="similar_logs.txt"):
    """
    Save the list of similar logs with labels and scores to a text file.

    :param results: List of dictionaries containing "raw_message", "label", and "score".
    :param filename: Name of the file to save the results.
    """
    with open(filename, "a", encoding="utf-8") as f:
        f.write("#" * 80 + "\n")  # Separator for readability
        f.write(f"Log query: {log_query}\n")
        f.write("#" * 80 + "\n")  # Separator for readability
        for entry in results:
            log_message = entry["raw_message"]
            label = entry["label"]
            score = entry["score"]

            # Convert label to string (if it's a list, join with commas)
            label_str = ", ".join(label) if isinstance(label, list) else label
            # Write to file
            f.write(f"Similar Log: {log_message}\n")
            f.write(f"Label: {label_str}\n")
            f.write(f"Score: {score:.4f}\n")  # Formatting score to 4 decimal places
            f.write("-" * 80 + "\n")  # Separator for readability
    print(f"Results saved to {filename}")


if __name__ == "__main__":
    # Adjust the path to your 'gather' directory
    gather_directory = DIRECTORY+"knn"

    # Create the index with mapping if it doesn't exist
    #create_index()

    # Ingest logs from the gather directory
    #ingest_logs(gather_directory)
    # Knn search of the logs
    log_example = ["Jan 23 07:07:01 inet-dns CRON[0]: pam_unix(cron:session): session opened for user jose by (uid=0)",
                   "Jan 24 03:56:47 inet-dns sshd[15085]: Did not receive identification string from 192.168.230.122 port 44004"]
    for log in log_example:
        similar_logs = search_similar_logs(log)
        save_results_to_file(similar_logs,log)
        print("\nlog:", log, "\nSIMILAR LOGS =", similar_logs)


"""
def parse_log_line(line):
    # Example regex for dovecot logs (adjust as needed)
    pattern = r'(?P<timestamp>\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<application>\w+)\s+(?P<process>[^:]+):\s+(?P<message>.+)'
    match = re.match(pattern, line)
    if match:
        data = match.groupdict()
        # Convert timestamp to standard datetime (assume current year)
        data['timestamp'] = datetime.strptime(f"{datetime.now().year} {data['timestamp']}", "%Y %b %d %H:%M:%S")
        return data
    return None

def ingest_logs(gather_dir):
    actions = []
    # Walk through gather directory
    for root, dirs, files in os.walk(gather_dir):
        for file in files:
            if file.endswith('.log'):
                host_name = root.split(os.sep)[1]  # Adjust based on actual path structure
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    for line in f:
                        parsed = parse_log_line(line)
                        if parsed:
                            # Optionally generate embedding here if model available
                            # parsed['embedding'] = generate_embedding(parsed['raw_message'])
                            parsed['host'] = host_name
                            parsed['raw_message'] = line.strip()
                            action = {
                                "_index": "cyber-logs",
                                "_source": parsed
                            }
                            actions.append(action)
    helpers.bulk(client, actions)

# Run ingestion
ingest_logs('gather')
"""
