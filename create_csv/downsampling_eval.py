import pandas as pd
import numpy as np

NORMAL_LABEL = 'normal_log' # O la etiqueta 'normal' exacta que uses (distingue mayúsculas/minúsculas)
PERCENT_TO_DROP_NORMAL = 0.50 # 80% de los logs 'normales' a eliminar (conservar el 20%)
CSV_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\downsampled_eval_log_data.csv"

# --- 1. Cargar el dataset ---
print(f"Cargando dataset desde: {CSV_PATH}...")
try:
    df = pd.read_csv(CSV_PATH)
    print(f"Dataset cargado exitosamente. Forma original: {df.shape}")
except FileNotFoundError:
    print(f"Error: El archivo '{CSV_PATH}' no fue encontrado. Por favor, verifica la ruta.")
    exit()

# --- 2. Verificar columnas ---
required_columns = ['log_message', 'source', 'label'] # Asegúrate de que 'log_message' es el nombre correcto de la columna
if not all(col in df.columns for col in required_columns):
    print(f"Error: Faltan una o más columnas requeridas ({required_columns}). Encontradas: {df.columns.tolist()}")
    exit()

# --- 3. Separar logs 'normales' y 'no normales' ---
df_normal = df[df['label'] == NORMAL_LABEL].copy()
df_other = df[df['label'] != NORMAL_LABEL].copy()

print(f"\nConteo original de logs '{NORMAL_LABEL}': {len(df_normal)}")
print(f"Conteo original de logs no-'{NORMAL_LABEL}': {len(df_other)}")

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

# Calcular cuántos logs normales adicionales podemos eliminar de este grupo
# Asegúrate de no eliminar más de los que tienes disponibles
num_normal_to_drop_from_remaining = int(len(df_normal) * PERCENT_TO_DROP_NORMAL) - (len(df_normal) - len(potential_normal_indices_to_drop)) # This line needs careful thought
# Correct calculation for num_normal_to_drop_from_remaining:
# Calculate total normal logs we want to keep = total_normal_logs * (1 - PERCENT_TO_DROP_NORMAL)
# Number to keep = total_normal_logs - num_normal_to_drop
# Number to keep = len(df_normal) * (1 - PERCENT_TO_DROP_NORMAL)
# Number to keep = (number of preserved logs) + (number of additional logs to keep from remaining)
# So, additional logs to keep from remaining = (total_normal_logs * (1 - PERCENT_TO_DROP_NORMAL)) - (number of preserved logs)

num_normal_to_keep_desired = int(len(df_normal) * (1 - PERCENT_TO_DROP_NORMAL))
# Ensure we keep at least the number of preserved logs if the desired number is smaller
num_normal_to_keep_actual = max(num_normal_to_keep_desired, len(indices_to_preserve_from_normal))

# The number of normal logs we need to drop from the 'potential_normal_indices_to_drop' set
num_to_drop_from_potential = len(potential_normal_indices_to_drop) - (num_normal_to_keep_actual - len(indices_to_preserve_from_normal))

# Ensure we don't try to drop a negative number or more than available
num_to_drop_from_potential = max(0, min(num_to_drop_from_potential, len(potential_normal_indices_to_drop)))


print(f"Logs normales disponibles para posible eliminación: {len(potential_normal_indices_to_drop)}")
print(f"Logs normales que se quieren mantener en total: {num_normal_to_keep_actual}")
print(f"Logs normales a eliminar de los restantes: {num_to_drop_from_potential}")


# --- 6. Seleccionar aleatoriamente índices de logs 'normales' para eliminar (de los no preservados) ---
indices_to_drop = np.random.choice(
    potential_normal_indices_to_drop,
    size=num_to_drop_from_potential,
    replace=False
)

print(f"Número de índices de '{NORMAL_LABEL}' seleccionados para eliminación: {len(indices_to_drop)}")

# --- 7. Crear el nuevo DataFrame downsampleado ---
# Empezamos con los logs no-normales
df_final_downsampled = df_other.copy()

# Añadimos los logs normales que hemos decidido preservar
df_final_downsampled = pd.concat([df_final_downsampled, preserved_normal_logs])

# Añadimos los logs normales restantes que NO han sido seleccionados para eliminar
# Get the indices of normal logs that were not preserved AND not selected to be dropped
remaining_normal_indices = potential_normal_indices_to_drop.difference(indices_to_drop)
df_final_downsampled = pd.concat([df_final_downsampled, df.loc[remaining_normal_indices]])

print(f"\nForma final del dataset después del downsampling: {df_final_downsampled.shape}")
print(f"Logs '{NORMAL_LABEL}' finales: {len(df_final_downsampled[df_final_downsampled['label'] == NORMAL_LABEL])}")
print(f"Logs no-'{NORMAL_LABEL}' finales: {len(df_final_downsampled[df_final_downsampled['label'] != NORMAL_LABEL])}")


# --- 8. Opcional: Mezclar el dataset final ---
df_final_downsampled = df_final_downsampled.sample(frac=1, random_state=42).reset_index(drop=True)

# --- 9. Guardar el nuevo dataset (opcional, pero recomendado) ---
OUTPUT_CSV_FILE_PATH = 'downsampled_eval_log_data.csv'
print(f"\nGuardando dataset downsampleado en: {OUTPUT_CSV_FILE_PATH}")
df_final_downsampled.to_csv(OUTPUT_CSV_FILE_PATH, index=False)
print("Downsampling completado y guardado!")

# --- Verificación Final (Opcional) ---
print("\nVerificando conteo de fuentes en el dataset final:")
final_source_counts = df_final_downsampled['source'].value_counts()
print(final_source_counts)

print("\nVerificando si todas las fuentes originales tienen al menos un log:")
original_sources = df['source'].unique()
missing_sources = [src for src in original_sources if src not in final_source_counts.index]
if not missing_sources:
    print("¡Éxito! Todas las fuentes originales están presentes en el dataset final.")
else:
    print(f"Advertencia: Las siguientes fuentes originales no tienen logs en el dataset final: {missing_sources}")

# Optional: Verify if there's at least one 'normal_log' per source, if they existed originally
for source_val in original_sources:
    normal_logs_for_source = df_final_downsampled[(df_final_downsampled['source'] == source_val) & (df_final_downsampled['label'] == NORMAL_LABEL)]
    if source_val in df_normal['source'].unique() and normal_logs_for_source.empty:
        print(f"Advertencia: La fuente '{source_val}' debería tener un log '{NORMAL_LABEL}' preservado, pero no se encontró.")