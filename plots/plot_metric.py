import json
import matplotlib.pyplot as plt
from sys import argv
LLM_PATH="C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\LLM\\classification_report_Llm_downsampled.json"
KNN_PATH="C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\Knn\\classification_report_Knn3_50k.json"
LLM_RAG_PATH="C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\LLM_RAG\\classification_report_Llm_rag_second_k_3.json"
METRIC="f1-score"
excluded_keys = {"accuracy", "macro avg", "weighted avg","escalated_command","attacker_vpn","wpscan","attacker_change_user", "dirb","traceroute","escalate", "webshell_cmd"}

def extract_precisions(data):
    return {key: data[key][METRIC] for key in data if key not in excluded_keys}
# Load JSON data from file
def load_file(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data
mode = argv[1].lower()
if mode=="knn":
    data = load_file(KNN_PATH)
    color="skyblue"
elif mode=="llm":
    data = load_file(LLM_PATH)
    color="orange"
else:
    data = load_file(LLM_RAG_PATH)
    color="green"
# Extract precision per label for each model


prec = extract_precisions(data)

# All unique labels from all models
all_labels = sorted(set(prec))
# Prepare data for plotting
vals = [prec.get(label, 0) for label in all_labels]

# Plot
x = range(len(all_labels))


plt.figure(figsize=(14, 8))
# Bars
#bars_knn = plt.bar([i - width for i in x], knn_vals, width=width, label='KNN')
#bars_llm = plt.bar(x, llm_vals, width=width, label='LLM')
bars = plt.bar( x, vals, width=0.2,color=color)
# Labels above bars
def annotate_bars(bars):
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, height + 0.01,
                 f'{height:.2f}', ha='center', va='bottom', fontsize=8)

#annotate_bars(bars_knn)
#annotate_bars(bars_llm)
annotate_bars(bars)
plt.xlabel("labels")
plt.ylabel(METRIC)
#plt.title(METRIC+" per Label for KNN, LLM and LLM_RAG")
plt.xticks(ticks=x, labels=all_labels, rotation=45, ha="right")
plt.ylim(0, 1.05)
#plt.legend( bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.grid(True, linestyle="--", alpha=0.5)
#plt.show()
plt.savefig(METRIC+"___"+mode+".jpeg")