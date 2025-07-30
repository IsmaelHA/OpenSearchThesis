from collections import defaultdict
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
import random
import json


def save_results_to_file(label_percentages, log_query, filename="similar_logs.txt"):
    """
    Save the list of similar logs with labels and scores to a text file.

    :param results: List of dictionaries containing "raw_message", "label", and "score".
    :param filename: Name of the file to save the results.
    """
    with open(filename, "a", encoding="utf-8") as f:
        f.write("#" * 80 + "\n")  # Separator for readability
        f.write(f"Log query: {log_query}\n")
        f.write("#" * 80 + "\n")  # Separator for readability
        for label, score in label_percentages.items():
            f.write(f"Label: {label}, Score: {score:.2f}%\n")
            f.write("-" * 80 + "\n")  # Separator for readability
        """for entry in results:
            #log_message = entry["raw_message"]
            label = entry["label"]
            score = entry["score"]

            # Convert label to string (if it's a list, join with commas)
            label_str = ", ".join(label) if isinstance(label, list) else label
            # Write to file
            #f.write(f"Similar Log: {log_message}\n")
            f.write(f"Label: {label_str}\n")
            # Formatting score to 4 decimal places
            f.write(f"Score: {score:.4f}\n")
            f.write("-" * 80 + "\n")  # Separator for readability"""
    print(f"Results saved to {filename}")


def analize_results(y_eval, y_pred,evaluator):
    labels = list(set(y_eval) | set(y_pred))
    # Matriz de confusión
    cm = confusion_matrix(y_eval, y_pred, labels=labels)
    print("Matriz de Confusión:")
    print(cm)

    # Reporte detallado (precisión, recall, F1)
    # print("\nReporte de Clasificación:")
    # print(classification_report(y_eval, y_pred,labels=labels))
    report_dict = classification_report(
        y_eval, y_pred, output_dict=True, labels=labels)

# Guardar como archivo JSON
    with open("classification_report_"+evaluator+".json", "w") as f:
        json.dump(report_dict, f, indent=4)

    # Create confussion matrix plot
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted", fontsize=14, fontweight='bold')
    plt.ylabel("Real", fontsize=14, fontweight='bold')
    plt.title("Confusion Matrix", fontsize=16, fontweight='bold', pad=20)

    plt.xticks(rotation=75, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    # plt.show()
    number = random.randint(1, 10000)
    plt.savefig("confusion_matrix_"+evaluator+str(number)+".png", dpi=300)
