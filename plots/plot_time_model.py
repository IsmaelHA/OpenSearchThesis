
import matplotlib.pyplot as plt

# Your dictionary
time={
    "KNN":0.105,
    "LLM":0.013,
    "LLM_RAG":0.108
}

# Extract data
models = list(time.keys())
times = list(time.values())

# Plot
plt.figure(figsize=(8, 5))
bars = plt.bar(models, times, color=['skyblue', 'lightgreen', 'salmon'])

plt.xlabel("Model")
plt.ylabel("Query Time (seconds)")
plt.title("Query Time per Model")
plt.ylim(0, max(times) + 0.02)
plt.grid(True, axis='y', linestyle='--', alpha=0.5)

# Annotate each bar with the time
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, height + 0.005,
             f'{height:.3f}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.show()
