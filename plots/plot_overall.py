import json
import matplotlib.pyplot as plt

# File paths
LLM_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\LLM\\classification_report_Llm_downsampled.json"
KNN_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\Knn\\classification_report_Knn3_50k.json"
LLM_RAG_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\LLM_RAG\\classification_report_Llm_rag_second_k_3.json"

# Load accuracy and weighted avg metrics from file
def load_model_metrics(path):
    with open(path, 'r') as f:
        data = json.load(f)
    weighted = data.get("weighted avg", {})
    return {
        "accuracy": data.get("accuracy", 0),
        "precision": weighted.get("precision", 0),
        "recall": weighted.get("recall", 0),
        "f1-score": weighted.get("f1-score", 0)
    }

# Load metrics for each model
metrics = {
    "KNN": load_model_metrics(KNN_PATH),
    "LLM": load_model_metrics(LLM_PATH),
    "LLM + RAG": load_model_metrics(LLM_RAG_PATH)
}

# Metrics to plot
metric_names = ["accuracy", "precision", "recall", "f1-score"]
x = range(len(metric_names))
width = 0.25

plt.figure(figsize=(10, 6))

# Plot bars for each model
for i, (model, vals) in enumerate(metrics.items()):
    values = [vals[m] for m in metric_names]
    positions = [pos + i * width for pos in x]
    bars = plt.bar(positions, values, width=width, label=model)
    
    # Annotate bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, height + 0.01,
                 f'{height:.4f}', ha='center', va='bottom', fontsize=8)

# Format plot
plt.xticks([pos + width for pos in x], metric_names)
plt.ylabel("Score")
plt.ylim(0, 1.05)
plt.title("Overall Accuracy, Precision, Recall and F1-score")
plt.legend(bbox_to_anchor=(1.02, 0.5))
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

