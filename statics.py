from collections import defaultdict

def analize_scores(items):
    label_scores = defaultdict(float)

    # Sumar scores por label
    for item in items:
        label_scores[item["label"]] += item["score"]

    # Score total para normalizar
    total_score = sum(label_scores.values())

    # Normalizar a porcentaje
    label_percentages = {
        label: score / total_score * 100
        for label, score in label_scores.items()
    }

    print("Porcentajes por label:")
    for label, percentage in label_percentages.items():
        print(f"  {label}: {percentage:.2f}%")

    # Aviso 1: normal_log no es mayor que el resto juntos
    normal_score = label_scores.get("normal_log", 0)
    others_score = total_score - normal_score

    if normal_score <= others_score:
        print("⚠️  Alerta: 'normal_log' no domina. El resto tiene más score total.")
    
    # Aviso 2: hay otros labels distintos a 'normal_log'
    if any(label != "normal_log" for label in label_scores):
        print("⚠️  Alerta: Se han detectado logs no normales (potenciales ataques).")

    # Devolver label más pesado
    most_likely = max(label_scores.items(), key=lambda x: x[1])
    print(f"✅ Label más probable: {most_likely[0]} ({most_likely[1]:.2f} score)")
    
    return label_percentages

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