
from datetime import datetime
from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer
import time
from constants import *
from ingest_pipeline import *
from search_methods import *
# Initialize OpenSearch client
client = OpenSearch(hosts=[{'host': 'localhost', 'port': 9200}], http_auth=('admin', 'Developer@123'), use_ssl=True,
                    verify_certs=False)
# You can change this to a cybersecurity-specific model if available
model = SentenceTransformer('all-MiniLM-L6-v2')

start_time = time.time()  # Inicia el conteo

# Create the index with mapping if it doesn't exist
#create_index(client)

# Ingest logs from the gather directory
#ingest_logs(GATHER_DIRECTORY,client,model)

# Knn search of the logs
log_examples = ["Jan 23 07:07:01 inet-dns CRON[0]: pam_unix(cron:session): session opened for user jose by (uid=0)",
                "Jan 24 03:56:47 inet-dns sshd[15085]: Did not receive identification string from 192.168.230.122 port 44004",
                "Jan 21 00:00:09 dnsmasq[3468]: reply 3x6-.596-.IunWTzebVlyAhhHj*ZfWjOBun1zAf*Wgpq-.YarqcF7oovex5JXZQp35nThgDU1Q3p3lT/-.DM6Vx/vcq3AkrO4Xh2kjojk8RCiDE2wjSv-.gY6ONv8eNmDck8gGwJ8fU3PPctbthfeDZT-.customers_2017.xlsx.email-19.kennedy-mendoza.info is 195.128.194.168"]
search_similar_logs(log_examples,client,model,k=5)

end_time = time.time()  # ⏱️ Termina el conteo
elapsed = end_time - start_time
print(f"⏱️ Tiempo de ejecución: {elapsed:.4f} segundos")