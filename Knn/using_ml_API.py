import time
from opensearchpy import OpenSearch
from opensearch_py_ml.ml_commons import MLCommonClient

# 1. Connect to OpenSearch
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'admin'),  # change if needed
    use_ssl=True,
    verify_certs=False
)

# 2. Create MLClient
ml_client = MLCommonClient(client)

# 3. Define the model
model_name = "huggingface/sentence-transformers/all-MiniLM-L6-v2"
model_version = "1.0.1"
model_format = "TORCH_SCRIPT"
model_group_id = "4E2cTZYB8OkuKVbXjBFl"  # Provided by you

model_payload = {
    "name": model_name,
    "version": model_version,
    "model_group_id": model_group_id,
    "model_format": model_format,
    "content": {
        "repository": "huggingface",
        "model_id": model_name  # Same name here
    }
}


# 4. Register model to OpenSearch
register_response = ml_client.register_pretrained_model(
    model_name, model_version, model_format, model_group_id)
model_id = register_response['model_id']

print(f"✅ Model registered successfully with ID: {model_id}")

# 5. Deploy the model
deploy_response = ml_client.deploy(model_id=model_id)
task_id = deploy_response['task_id']

print(f"Deployment started, Task ID: {task_id}")

# 6. Wait for deployment to finish

print(" Waiting for model to be deployed...")
while True:
    status = ml_client.get_task(task_id)
    task_status = status['state']

    if task_status in ["COMPLETED", "FAILED"]:
        print(f"Deployment finished with status: {task_status}")
        break
    else:
        print(f"Deployment still in progress... Current state: {task_status}")
        time.sleep(5)

# 7. Inference API: Encode a log message
log_message = "Jan 23 07:07:01 inet-dns CRON[14404]: pam_unix(cron:session): session opened for user root."

inference_payload = {
    "input": {
        "text": [log_message]
    }
}

inference_response = ml_client.predict(
    model_id=model_id, body=inference_payload)

# 8. Get the embedding
embedding_vector = inference_response['results'][0]

print(
    f"✅ Log encoded! Embedding vector (first 5 values): {embedding_vector[:5]}")
