import matplotlib.pyplot as plt
from sys import argv
query_times={
    "1":0.753,
    "5":0.176,
    "10":0.104,
    "25":0.087,
    "50":0.087,
    "100":0.09,
    "200":0.095,
    "400":0.155,
}
knn_times={
    "3":0.133,
    "5":0.141,
    "7":0.214
}
knn_accuracy={
    "3":0.9619,
    "5":0.9523,
    "7":0.9521
}
mode = argv[1].lower()
if mode=="knn":
    query_times=knn_times
# Convert keys to integers
batch_sizes = [int(k) for k in query_times.keys()]
times = list(query_times.values())

# Plot
plt.figure(figsize=(10, 5))
plt.plot(batch_sizes, times, marker='o', linestyle='-', color='teal')
plt.xlabel("K")
plt.ylabel("Query Time (seconds)")
#plt.title("Query Time vs. Batch Size in LLM_RAG")
plt.grid(True, linestyle="--", alpha=0.5)
plt.xticks(batch_sizes)
# Annotate each point with batch size and time
for x, y in zip(batch_sizes, times):
    plt.text(x, y + 0.01, f'{y:.3f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()