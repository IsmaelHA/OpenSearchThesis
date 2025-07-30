from opensearchpy import OpenSearch
from groq import Groq
from constants import GROQ_KEY
import pandas as pd
from sklearn.model_selection import train_test_split


class ClientFactory:
    @staticmethod
    def get_open_search_client():
        return OpenSearch(hosts=[{'host': 'localhost', 'port': 9200}], http_auth=('admin', 'Developer@123'), use_ssl=True, verify_certs=False, timeout=60)

    @staticmethod
    def get_groq_client():
        return Groq(api_key=GROQ_KEY)


class DataPreprocess:
    @staticmethod #Separate and return train and eval df 
    def load_and_prepare_data(csv_path):
        df = pd.read_csv(csv_path)
        print("Total samples:", len(df))
        df = df.sample(frac=1, random_state=73).reset_index(drop=True)
        train_df, eval_df = train_test_split(
            df, test_size=0.2, shuffle=True, random_state=42, stratify=df['label'])
        print("Training samples:", len(train_df))
        print(train_df['label'].value_counts())
        print("Evaluation samples:", len(eval_df))
        print(eval_df['label'].value_counts())
        return train_df, eval_df
    
    @staticmethod # Separate the train and eval data  and save them in diferent csv
    def separate_data_csv(csv_path):
        train_df, eval_df = DataPreprocess.load_and_prepare_data(csv_path)
        train_df.to_csv('train_data.csv', index=False)
        eval_df.to_csv('eval_data.csv', index=False)


    @staticmethod
    def load_data(csv_path):
        return pd.read_csv(csv_path)
        
