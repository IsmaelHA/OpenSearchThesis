
# OpenSearch index name for vectorized logs
INDEX_NAME = "russellmitchell-logs-cosine"

# Directory containing gathered raw logs
GATHER_DIRECTORY = ""

# Directory with internet/network configuration files
INET_DIRECTORY = ""

# Transformer model ID for embeddings
MODEL_ID = ""

# Embedding vector size (MiniLM = 384 dims)
VECTOR_SIZE = 384

# Number of logs processed per file batch
LOGS_PER_FILE = 100

# File containing attack annotations
ATTACKS_LOG_FILE = "attack.log"

# API key for Groq (if used)
GROQ_KEY = ""

# Path to main CSV dataset
CSV_PATH = ""

# Path to training CSV subset
TRAIN_CSV = ""

# Path to evaluation CSV subset
EVAL_CSV = ""

# LLM model name for classification
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"

# Endpoint URL for LLM API
LLM_URL = ""