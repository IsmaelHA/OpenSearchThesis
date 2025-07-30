import matplotlib.pyplot as plt

# KNN accuracy values
knn_accuracy = {
    "3": 0.9619,
    "5": 0.9523,
    "7": 0.9521
}

# Extract keys and values
k_values = list(knn_accuracy.keys())
accuracies = list(knn_accuracy.values())

# Create bar plot
plt.figure(figsize=(6, 4))
bars = plt.bar(k_values, accuracies)

# Add accuracy values above bars
for bar, accuracy in zip(bars, accuracies):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001, f"{accuracy:.4f}", 
             ha='center', va='bottom')

# Plot settings
plt.ylim(0.94, 0.97)
plt.xlabel("k value")
plt.ylabel("Accuracy")
#plt.title("KNN Accuracy for Different k Values")
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
