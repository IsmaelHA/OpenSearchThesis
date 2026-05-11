# OpenSearchThesis

**Bachelor Thesis: Evaluation of Large Language Models for Intrusion Detection Systems – Ismael Hernández Alarcón**

This repository contains the implementation of my TFG (Trabajo de Fin de Grado), focused on **log-based intrusion detection** using three approaches:
1. **KNN-based Detection** (baseline with semantic embeddings)  
2. **LLM-based Detection** (direct classification with explanations)  
3. **LLM + Retrieval-Augmented Generation (RAG)** (context-aware detection with explanations)

The system combines **OpenSearch Vector Database, Transformers and Large Language Models** to classify system logs as benign or malicious, providing both predictions and human-readable explanations.

In TFG_Ismael_Hernandez_Alarcon.pdf is the Thesis with a extended summary in Spanish.

---

## 📂 Project Structure
```text
├── create_csv/ - Scripts for CSV creation and preprocessing from raw logs
├── opensearch/ - YAML config for opensearch docker
├── Knn/  - KNN IDS implementation and evaluation
├── LLM/  - LLM IDS implementation and evaluation
├── LLM_RAG/  - LLM + RAG IDS with contextual retrieval implementation and evaluation
├── config/   - configs for embedding pipeline in opensearch and requirements for python
├── plots/  - Scripts to make different plots
├── constant.py - Script with all the constants needed, you need to change some of the variables
└── main.py - Main script and the only one you need to execute
```
---

## Usage

### 1. Start OpenSearch

```bash
docker-compose up -d
```
This launches:

OpenSearch node (v2.19) and Dashboard for monitoring

Then:
```bash
python .\config\set_up_embedding_pipeline.py
```
Set up the pipeline and the transformer to ingest the logs and create the vectors.
### 2. Install Python requirements

Create a virtual environment (recommended) and install dependencies from requirements.txt:
```bash
python3 -m venv .venv
```

```bash
.\.venv\Scripts\activate
```

#### Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Creating the Index and Ingest the logs to Opensearch

Configure the vector database (HNSW + FAISS + cosine similarity) and insert embeddings:
```bash
python main.py ingestion
```
If the ingestion is not working, try to config the pipeline manually, the steps needed are in config/set_up_embedding_pipeline.txt

### 4. Running the Scenarios
🔹 KNN-based IDS

Evaluation of Knn scenario:

```bash
python main.py knn
```

🔹 LLM-based IDS

Evaluation of LLM scenario:

```bash
python main.py llm
```

🔹 LLM + RAG IDS

Evaluation of LLM + RAG scenario:

```bash
python main.py llm_rag
```

Each script produces:

Classification report in JSON with all the metrics mentioned behind, overall and per class.

Confusion matrix saved as .png

File with the explanations of the anomalies

Times printed in the standar output


---

## 📊 Evaluation Metrics

The system evaluates the following metrics across all scenarios:

Accuracy → overall correctness of classification

Precision → ratio of true positives over predicted positives

Recall → ratio of true positives over actual positives

F1-score → harmonic mean of precision and recall


## 🗂 Dataset
Experiments use the **AIT Log Data Set V2.0** (Russell Mitchell subset, ~14GB, 11M logs).  

Preprocessing in create_csv produces a **CSV** with:
- `source`: service/host (mail, vpn, apache, …)  
- `log_message`: raw log entry  
- `label`: attack type or `normal_log`  

⚠️ Due to imbalance, in create_csv/, there are some scripts to **downsample** normal logs as I did. Stratified 80/20 split is used for training/evaluation.

---

