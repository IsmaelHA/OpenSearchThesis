import pandas as pd
from sklearn.utils import resample
CSV_PATH = "C:\\Users\\elcrio\\Desktop\\TFG\\src\\OpenSearchThesis\\downsampled_eval_log_data.csv"
def downsample_diverse(csv_path: str, output_path: str, sample_size: int = 1000):
    # Load CSV
    df = pd.read_csv(csv_path)

    # Ensure we don't remove rare (label, source) combinations
    grouped = df.groupby(['label', 'source'])
    
    # Take at least 1 sample from each group first
    core_samples = grouped.apply(lambda x: x.sample(1)).reset_index(drop=True)
    
    # Drop those rows from original
    remaining_df = df.drop(core_samples.index)

    # Calculate remaining quota
    remaining_quota = sample_size - len(core_samples)
    
    # Sample the rest randomly from the remaining set
    if remaining_quota > 0:
        rest_sample = remaining_df.sample(n=remaining_quota, random_state=42)
        final_sample = pd.concat([core_samples, rest_sample])
    else:
        final_sample = core_samples.sample(n=sample_size, random_state=42)

    # Shuffle the final dataset
    final_sample = final_sample.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    final_sample.to_csv(output_path, index=False)
    print(f"✅ Downsampled to {len(final_sample)} rows and saved to {output_path}")

train_df = pd.read_csv('downsampled_eval_log_data.csv')
print("Training samples:", len(train_df))
print(train_df.head(5))
print(train_df["label"].value_counts())
# downsample_diverse(CSV_PATH,'downsampled_eval_log_data.csv')