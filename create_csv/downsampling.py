import pandas as pd
NORMAL_LABEL = 'normal_log'           # Or whatever your exact 'normal' label is (case-sensitive)
PERCENT_TO_DROP_NORMAL = 0.80     # 80% of the normal logs to drop (keep 70%)
CSV_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\eval_data.csv"
# --- 1. Load the dataset ---
print(f"Loading dataset from: {CSV_PATH}...")
try:
    df = pd.read_csv(CSV_PATH)
    print(f"Dataset loaded successfully. Original shape: {df.shape}")
except FileNotFoundError:
    print(f"Error: The file '{CSV_PATH}' was not found. Please check the path.")
    exit()

# --- 2. Verify columns ---
required_columns = ['log_message', 'source', 'label']
if not all(col in df.columns for col in required_columns):
    print(f"Error: Missing one or more required columns ({required_columns}). Found: {df.columns.tolist()}")
    exit()

# --- 3. Identify indices of normal logs ---
# Get the boolean mask for normal logs
is_normal = (df['label'] == NORMAL_LABEL)

# Get the actual indices of rows labeled 'normal'
normal_indices = df[is_normal].index

print(f"\nOriginal count of '{NORMAL_LABEL}' logs: {len(normal_indices)}")
print(f"Original count of non-'{NORMAL_LABEL}' logs: {len(df) - len(normal_indices)}")
# --- 4. Identificar logs 'normales' a preservar por 'source' ---
# Crear un DataFrame vacío para almacenar los logs 'normales' que deben conservarse
preserved_normal_logs = pd.DataFrame()

# Iterar sobre cada 'source' única en el DataFrame original
for source_val in df_normal['source'].unique():
    # Obtener todos los logs 'normales' para esta 'source'
    normal_logs_from_source = df_normal[df_normal['source'] == source_val]

    if not normal_logs_from_source.empty:
        # Seleccionar aleatoriamente 1 log 'normal' de esta 'source' para preservar
        # Si solo hay 1 o menos, se seleccionará ese 1 (o ninguno si está vacío, aunque el 'if not empty' lo evita)
        # using .sample(n=1) is safer and handles cases where there's only 1 log for that source
        preserved_log = normal_logs_from_source.sample(n=1, random_state=42)
        preserved_normal_logs = pd.concat([preserved_normal_logs, preserved_log])

# Obtener los índices de los logs normales que DEBEMOS preservar
indices_to_preserve_from_normal = preserved_normal_logs.index.tolist()
print(f"\nNúmero de logs '{NORMAL_LABEL}' preservados (uno por cada source única): {len(indices_to_preserve_from_normal)}")

# --- 5. Determinar los logs 'normales' restantes de los cuales podemos eliminar ---
# Indices de todos los logs normales EXCEPTO los que ya hemos decidido preservar
potential_normal_indices_to_drop = df_normal.index.difference(indices_to_preserve_from_normal)

# --- 4. Determine how many normal logs to drop ---
num_normal_to_drop = int(len(normal_indices) * PERCENT_TO_DROP_NORMAL)
print(f"Number of '{NORMAL_LABEL}' logs to drop: {num_normal_to_drop}")

# --- 5. Randomly select indices of normal logs to drop ---
# We sample from the `normal_indices` to get the indices of rows we want to remove
import numpy as np # Used for random choice, potentially more memory efficient than df.sample on large index sets
indices_to_drop = np.random.choice(normal_indices, size=num_normal_to_drop, replace=False)

print(f"Number of indices selected for dropping: {len(indices_to_drop)}")

# --- 6. Drop the selected rows from the original DataFrame ---
# This modifies df in-place, which is good for memory
df.drop(indices_to_drop, inplace=True)

print(f"\nFinal dataset shape after downsampling normal logs: {df.shape}")
print(f"Total rows dropped: {num_normal_to_drop}") # This will match the calculation

# --- 7. Optional: Shuffle the final dataset ---
# It's good practice to shuffle if you plan to split it further or train models on it.
# This operation creates a copy, but it's on the already reduced DataFrame
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# --- 8. Save the new dataset (optional, but recommended) ---
OUTPUT_CSV_FILE_PATH = 'downsampled_eval_log_data.csv'
print(f"\nSaving downsampled dataset to: {OUTPUT_CSV_FILE_PATH}")
df.to_csv(OUTPUT_CSV_FILE_PATH, index=False)
print("Downsampling complete and saved!")

# --- Verification (Optional) ---
print("\nVerifying label distribution in final dataset:")
print(df['label'].value_counts())