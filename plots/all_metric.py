import json
import matplotlib.pyplot as plt
from sys import argv

LLM_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\LLM\\classification_report_Llm_downsampled.json"
KNN_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\Knn\\classification_report_Knn3_50k.json"
LLM_RAG_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\LLM_RAG\\classification_report_Llm_rag_second_k_3.json"

# List of metrics to plot
METRICS = ["f1-score", "precision", "recall"]
excluded_keys = {"accuracy", "macro avg", "weighted avg", "escalated_command", "attacker_vpn", "wpscan", "attacker_change_user", "dirb", "traceroute", "escalate", "webshell_cmd"}

def extract_metrics(data, metrics_list):
    """
    Extracts specified metrics for each label, excluding specified keys.
    Returns a dictionary where keys are labels and values are dictionaries
    containing the extracted metrics.
    """
    extracted_data = {}
    for key in data:
        if key not in excluded_keys:
            extracted_data[key] = {metric: data[key].get(metric, 0) for metric in metrics_list}
    return extracted_data

# Load JSON data from file
def load_file(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    # Check if a mode argument is provided
    if len(argv) < 2:
        print("Usage: python your_script_name.py [knn|llm|llm_rag]")
        exit(1)

    mode = argv[1].lower()

    if mode == "knn":
        data = load_file(KNN_PATH)
        plot_title_prefix = "KNN Model"
    elif mode == "llm":
        data = load_file(LLM_PATH)
        plot_title_prefix = "LLM Model"
    elif mode == "llm_rag":
        data = load_file(LLM_RAG_PATH)
        plot_title_prefix = "LLM_RAG Model"
    else:
        print(f"Invalid mode: {mode}. Please choose 'knn', 'llm', or 'llm_rag'.")
        exit(1)

    # Extract all required metrics for the selected model
    extracted_model_metrics = extract_metrics(data, METRICS)

    # All unique labels
    all_labels = sorted(set(extracted_model_metrics.keys()))

    # Prepare data for plotting
    f1_vals = [extracted_model_metrics.get(label, {}).get("f1-score", 0) for label in all_labels]
    precision_vals = [extracted_model_metrics.get(label, {}).get("precision", 0) for label in all_labels]
    recall_vals = [extracted_model_metrics.get(label, {}).get("recall", 0) for label in all_labels]

    # Plotting setup
    plt.figure(figsize=(16, 9)) # Increased figure size for better readability
    
    bar_width = 0.2
    x = range(len(all_labels)) # Base x-coordinates for each label

    # Adjust x-coordinates for each set of bars to group them
    r1 = [i - bar_width for i in x]
    r2 = x
    r3 = [i + bar_width for i in x]

    # Create bars for each metric
    bars_precision = plt.bar(r1, precision_vals, color='skyblue', width=bar_width,label='Precision')
    bars_recall = plt.bar(r2, recall_vals, color='orange', width=bar_width, label='Recall')
    bars_f1 = plt.bar(r3, f1_vals, color='lightgreen', width=bar_width, label='F1-score' )

    # Labels above bars
    def annotate_bars(bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, height + 0.01,
                     f'{height:.2f}', ha='center', va='bottom', fontsize=7) # Smaller font size for annotations

    annotate_bars(bars_f1)
    annotate_bars(bars_precision)
    annotate_bars(bars_recall)

    plt.xlabel("Labels", fontsize=10)
    plt.ylabel("Score", fontsize=10)
    #plt.title(f"{plot_title_prefix}: F1-score, Precision, and Recall per Label", fontsize=14)
    
    # Set x-ticks to be in the middle of the grouped bars
    plt.xticks(ticks=x, labels=all_labels, rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.ylim(0, 1.05)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 0.5), fontsize=10) # Legend outside the plot
    plt.tight_layout(rect=[0, 0, 0.9, 1]) # Adjust layout to make space for the legend
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.savefig(f"metrics_combined_{mode}.jpeg", dpi=300) # Save with higher DPI
    plt.show()