from sys import argv
import time
from constants import *
from Knn.open_search_ingestion_pipeline import *
from statics_methods import *
from Knn.search import KnnEvaluator
from LLM.search_async import LlmEvaluator
from LLM_RAG.search_async import LlmRagEvaluator
# Initialize OpenSearch client
open_search_client = ClientFactory.get_open_search_client()
# Create the index with mapping if it doesn't exist
create_index(open_search_client)
start_time = time.time() 
mode = argv[1].lower()# "ingestion", "Knn", "LLM", "LLM_RAG"
if mode == 'ingestion':
    train_df = DataPreprocess.load_data(TRAIN_CSV)
    print("Training samples:", len(train_df))
    print(train_df.head(5))
    print(train_df["source"].value_counts())
    start_time = time.time()
    # Ingest logs 
    ingest_batches_from_csv_pipeline(train_df, open_search_client)
    medium_time = time.time()
    ingest_time = medium_time - start_time
    print(f"⏱️ ingestion time: {ingest_time:.4f} seconds")
else:
    if mode == "knn":
        evaluator = KnnEvaluator(open_search_client)
    elif mode == "llm":
        evaluator = LlmEvaluator()
    elif mode == "llm_rag":
        evaluator = LlmRagEvaluator(open_search_client)
    else:
        raise ValueError(
            "Unknown mode, Modes: knn, llm, llm_rag\n Usage: python main.py [ingestion|knn|llm|llm_rag]")
    eval_df = DataPreprocess.load_data(EVAL_CSV)
    print(eval_df["label"].value_counts())
    evaluator.evaluate(eval_df,k=3)
    #for k in [3,5,7]:
    #    evaluator.evaluate(eval_df,k)
    end_time = time.time()  
    elapsed = end_time - start_time
    print(f"⏱️ eval time: {elapsed:.4f} seconds")

end_time = time.time()  
elapsed = end_time - start_time
print(f"⏱️ Total execution time: {elapsed:.4f} seconds")
