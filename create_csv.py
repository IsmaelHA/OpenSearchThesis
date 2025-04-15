import os
import pandas as pd
from sklearn.model_selection import train_test_split
import csv
from constants import LOGS_PER_FILE
from ingest_pipeline import get_label,get_labels
def ingest_logs_to_csv_stream(gather_dir, output_csv):
    """
    Traverse the 'gather_dir', read .log files, extract the log message and its label 
    (using associated label files), and write each row directly to a CSV file.
    
    :param gather_dir: Directory containing the log files.
    :param output_csv: Output CSV file path.
    """
    
    # Open the CSV file in write mode (using "w" mode) and create a CSV DictWriter.
    with open(output_csv, "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["log_message", "label"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()  # Write column headers once.

        # Traverse the logs folder recursively
        for root, dirs, files in os.walk(gather_dir):
            for file in files:
                if ".log" in file:
                    file_path = os.path.join(root, file)
                    # Apply filtering conditions as used in your ingestion pipeline
                    if "attacker" in file_path:
                        continue
                    if "logs" not in file_path:
                        continue

                    # Retrieve labels from associated file (if it exists)
                    labels = get_labels(file_path)
                    with open(file_path, 'r', encoding='utf-8') as log_f:
                        for line_number, line in enumerate(log_f, 1):
                            line = line.strip()
                            if not line:
                                continue
                            if line_number > LOGS_PER_FILE:
                                break
                            
                            # Get the label for the current line using your get_label function.
                            log_label = get_label(labels, line_number)
                            
                            # Write the log and label immediately to CSV
                            writer.writerow({
                                "log_message": line,
                                "label": log_label
                            })
                            
    print(f"Logs have been ingested and written to '{output_csv}'.")

def split_dataset():
    # Load the CSV file into a DataFrame
    df = pd.read_csv("C:\\Users\\elcrio\\Desktop\\TFG\\ingested_logs.csv")

    # Optionally, inspect the DataFrame
    print(df.head())
    print("Total samples:", len(df))

    # Split the DataFrame into train and evaluation sets
    # For example: 80% for training and 20% for evaluation
    train_df, eval_df = train_test_split(df, test_size=0.2, random_state=42)

    print("Training samples:", len(train_df))
    print("Evaluation samples:", len(eval_df))

# Example usage:
if __name__ == "__main__":
    gather_directory = "C:\\Users\\elcrio\\Desktop\\TFG\\gather"  # Adjust path as needed.
    output_csv_file = "C:\\Users\\elcrio\\Desktop\\TFG\\ingested_logs.csv"
    ingest_logs_to_csv_stream(gather_directory, output_csv_file)
    split_dataset()
