import pandas as pd
import re
NORMAL_LABEL = 'normal_log'           # Or whatever your exact 'normal' label is (case-sensitive)
PERCENT_TO_DROP_NORMAL = 0.30     # 30% of the normal logs to drop (keep 70%)
CSV_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\downsampled_log_data.csv"
# --- 1. Load the dataset ---
print(f"Loading dataset from: {CSV_PATH}...")
try:
    df = pd.read_csv(CSV_PATH)
    print(f"Dataset loaded successfully. Original shape: {df.shape}")
except FileNotFoundError:
    print(f"Error: The file '{CSV_PATH}' was not found. Please check the path.")
    exit()

pattern_has_letter = r'[a-zA-Z]'
rows_to_keep = df['log_message'].str.contains(pattern_has_letter, na=False) # na=False trata los NaN como si no tuvieran letras

# Las filas que queremos eliminar son las que NO tienen letras
df_filtered = df[rows_to_keep].copy() # Usar .copy() para evitar SettingWithCopyWarning
df_filtered.to_csv(CSV_PATH, index=False)