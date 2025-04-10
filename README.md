# Thalassa - Sakarya University AI Assistant (OpenAI version)

Thalassa is an advanced AI-powered chatbot designed to assist Sakarya University students. It uses a **Turkish data store** and leverages Retrieval-Augmented Generation (RAG) with the **OpenAI API**. The system employs **multilingual models** for embedding and context re-ranking, conversational memory, and date awareness to provide accurate, contextually relevant, and natural-sounding responses in the user's language (Turkish/English).

screenshots
![](./screenshots/Screenshot1.png)
![](./screenshots/Screenshot2.png)

## Overview (Multilingual Component Pipeline)

This version works directly with Turkish source documents and utilizes specialized multilingual components for improved cross-lingual understanding:

1.  **Data Preparation (Offline):** Original Turkish `.txt` documents reside in the `extracted_texts/` folder.
2.  **Indexing (Offline):** `reload.sh` merges the Turkish texts and builds a FAISS index using embeddings from a **multilingual sentence transformer** (`paraphrase-multilingual-mpnet-base-v2` by default) generated from the **Turkish text**.
3.  **Session Management:** Frontend manages a `session_id` for conversational context.
4.  **Language Detection:** Backend detects the user's query language (TR/EN).
5.  **Query Translation (for Search/Rank):** Non-English queries are translated to English (via MyMemory API) to serve as a stable anchor for cross-lingual retrieval and ranking.
6.  **Context Retrieval (FAISS):** The **English query embedding** searches the FAISS index (containing **Turkish text embeddings**) to retrieve initial candidates (cross-lingual search).
7.  **Context Re-ranking (Cross-Encoder):** A **multilingual Cross-Encoder** (`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` by default) re-ranks the retrieved **Turkish chunks** based on relevance to the **English query**.
8.  **Final Context Selection:** The top `FINAL_CONTEXT_K` **Turkish chunks** are selected.
9.  **Conversation History & Date:** Recent history (in-memory) and current date are retrieved.
10. **Prompt Construction:** A detailed prompt is sent to OpenAI including system instructions, few-shot examples, current date, the retrieved **Turkish context**, conversation history, and the **original user query**.
11. **OpenAI API Call:** The prompt instructs the LLM (e.g., GPT-3.5/4) to generate an answer in the **same language as the original query**, understanding the Turkish context.
12. **History Update & Response:** The interaction is stored, and the final answer (in the user's language) and `session_id` are sent to the frontend.

## Key Features

- **Works with Turkish Source Data:** Directly indexes and retrieves from Turkish documents.
- **Multilingual RAG Components:** Uses multilingual embedding and cross-encoder models for better cross-lingual understanding.
- **State-of-the-Art LLM:** Leverages OpenAI models via API.
- **Conversational Memory:** Remembers recent interactions per session using session IDs.
- **Date Awareness:** Prioritizes upcoming dates and handles past dates intelligently.
- **Accurate Language Handling:** Understands Turkish/English queries, responds in the user's original language.
- **Few-Shot Prompting:** Guides LLM behavior with examples for complex tasks like date logic and name recall.
- **User-Friendly Interface:** React-based chat interface with MUI components.
- **Asynchronous Backend:** Efficient request handling with FastAPI.

## Technology Stack

- **Backend:**
  - Python 3.x
  - FastAPI
  - **OpenAI Python Library**
  - **Sentence Transformers** (for embedding & cross-encoder models)
  - FAISS (CPU/GPU)
  - **Langdetect**
  - **Requests** (for MyMemory API)
  - Numpy
  - Uvicorn
  - python-dotenv
- **Frontend:**
  - React
  - JavaScript
  - Material UI (MUI)
  - Axios
  - React Spinners
  - Lodash.debounce
- **AI Models:**
  - Generation: OpenAI (GPT-3.5 Turbo, GPT-4, etc. - configurable)
  - Embedding: `paraphrase-multilingual-mpnet-base-v2` (Multilingual - configurable)
  - Re-ranking: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (Multilingual - configurable)
- **Vector Store:** FAISS
- **Translation Service (Query):** MyMemory API

## Project Structure (Based on Image)

.
├── backend/
│ ├── app/
│ │ ├── init.py
│ │ ├── ai_response.py # Handles OpenAI calls, prompt construction
│ │ ├── faiss_search.py # Handles FAISS search & cross-encoder re-ranking
│ │ ├── main.py # FastAPI app, endpoints, history management
│ │ └── translation.py # Language detection & query translation
│ ├── data/
│ │ ├── faiss_index.bin # FAISS index (built from Turkish embeddings)
│ │ └── metadata.npy
│ ├── extracted_texts/ # <<< Turkish source .txt files
│ ├── utils/
│ │ ├── init.py
│ │ ├── create_faiss_index.py # Creates index using multilingual embedder on TEXT_FOLDER
│ │ └── merge_txt_files.py # Merges files in TEXT_FOLDER
│ └── venv/ # Python Virtual Environment
│
├── frontend/
│ ├── node_modules/
│ ├── public/
│ │ ├── index.html
│ │ ├── thalassa.ico
│ │ └── thalassa.png
│ ├── src/
│ │ ├── components/
│ │ │ ├── ChatWindow.jsx
│ │ │ ├── Header.jsx
│ │ │ ├── Message.jsx
│ │ │ ├── TypingIndicator.jsx
│ │ │ └── WelcomeModal.jsx
│ │ ├── hooks/
│ │ │ └── useChat.js # Handles chat state, API calls, session ID
│ │ ├── styles/
│ │ │ ├── global.css
│ │ │ └── theme.js
│ │ └── utils/ # (Seems unused based on App.jsx/useChat.js)
│ │ └── api.js
│ │ ├── App.jsx # Main application component
│ │ └── index.js # React entry point
│ ├── .gitignore
│ ├── package-lock.json
│ └── package.json
│
├── .env # API keys, model names, paths, RAG params
├── .gitignore
├── nohupt.out # Log file from nohup (if used)
├── README.md # This file
├── reload.sh # Rebuilds FAISS index from TEXT_FOLDER
├── requirements.txt # Backend Python dependencies
├── run.sh # Starts the backend server
└── translate_files.py # Utility script for translating files (not part of runtime)

## Setup and Installation

1.  **Clone Repository:**

    ```bash
    git clone <your-repository-url>
    cd <repository-directory>/backend # Navigate to backend first
    ```

2.  **Ensure Turkish Data:** Place your original Turkish `.txt` files in the `backend/extracted_texts/` directory.

3.  **Get OpenAI API Key:** Obtain an API key from [https://openai.com/](https://openai.com/).

4.  **Backend Setup:**

    - Create and activate a Python virtual environment:
      ```bash
      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      ```
    - Install Python dependencies:
      ```bash
      pip install -r requirements.txt
      ```
      _(This will install FastAPI, Uvicorn, OpenAI, Sentence Transformers, FAISS, etc.)_
    - Create a `.env` file in the `backend/` directory (or project root if scripts expect it there - adjust paths in scripts if needed). Configure it:

      ```env
      OPENAI_API_KEY="your_openai_api_key_here"

      # --- Ensure TEXT_FOLDER points to your Turkish data ---
      TEXT_FOLDER="extracted_texts"

      # --- Specify Multilingual Models ---
      EMBEDDING_MODEL="paraphrase-multilingual-mpnet-base-v2"
      CROSS_ENCODER_MODEL="cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

      # Optional: Adjust RAG/History parameters
      # OPENAI_MODEL="gpt-3.5-turbo"
      # FAISS_RETRIEVAL_K=10
      # FINAL_CONTEXT_K=4
      # MAX_HISTORY_TURNS=3
      ```

    - **IMPORTANT:** Build the FAISS index from the Turkish data:
      ```bash
      bash reload.sh
      ```
      _(This merges Turkish files, then runs `create_faiss_index.py` using the multilingual `EMBEDDING_MODEL`.)_

5.  **Frontend Setup:**
    - Navigate to the frontend directory:
      ```bash
      cd ../frontend # Go up one level from backend, then into frontend
      ```
    - Install Node.js dependencies:
      ```bash
      npm install
      # or
      # yarn install
      ```

## Usage

1.  **Start Backend:**

    - Navigate to the `backend/` directory.
    - Activate virtual environment (`source venv/bin/activate`).
    - Ensure `.env` is configured.
    - Run the backend server:
      ```bash
      bash run.sh
      ```
      _(Starts FastAPI on http://localhost:8000 by default)_

2.  **Start Frontend:**

    - Open a **new terminal**.
    - Navigate to the `frontend/` directory.
    - Start the React development server:
      ```bash
      npm start
      # or
      # yarn start
      ```

3.  **Interact:** Open your web browser and navigate to `http://localhost:3000` (or the port specified by the React server). Chat with Thalassa!

## Scripts (Located in `backend/`)

- **`run.sh`:** Activates the Python virtual environment and starts the FastAPI backend server using Uvicorn with auto-reload.
- **`reload.sh`:** Deletes existing FAISS index/metadata, merges `.txt` files in `TEXT_FOLDER` (Turkish), and runs `utils/create_faiss_index.py` to build a new FAISS index using the configured multilingual `EMBEDDING_MODEL`. **Run this script** whenever you modify the Turkish text files or change the `EMBEDDING_MODEL`.
- **`translate_files.py`:** (Optional Utility) A separate script to translate files using the MyMemory API (useful if you wanted to switch to the English-context approach later). Not part of the core runtime for this multilingual setup.

## Configuration (`backend/.env` file)

- `OPENAI_API_KEY`: **(Required)** Your secret API key from OpenAI.
- `TEXT_FOLDER`: **(Required)** Path to the directory containing your **Turkish** source `.txt` files (default: `extracted_texts`).
- `OPENAI_MODEL`: (Optional) OpenAI model identifier (default: "gpt-3.5-turbo").
- `EMBEDDING_MODEL`: (Optional) Multilingual Sentence Transformer model for FAISS indexing and query embedding (default: "paraphrase-multilingual-mpnet-base-v2").
- `CROSS_ENCODER_MODEL`: (Optional) **Multilingual** Cross-encoder model for re-ranking retrieved context (default: "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1").
- `FAISS_RETRIEVAL_K`: (Optional) Number of initial candidates retrieved from FAISS (default: 10).
- `FINAL_CONTEXT_K`: (Optional) Number of chunks sent to LLM after re-ranking (default: 4).
- `MAX_HISTORY_TURNS`: (Optional) Number of user/assistant message pairs remembered per session (default: 3).

## Workflow Summary

User Input (TR/EN) -> Frontend (`useChat`) -> Backend API (`/chat`) -> Detect Language -> Translate Query to EN (if needed) -> Search FAISS (TR Index) w/ EN Query Embedding -> Retrieve Initial TR Chunks -> Re-rank (EN Query, TR Chunks) w/ Multilingual Cross-Encoder -> Select Top TR Chunks -> Get History & Current Date -> Construct Prompt (w/ TR Context, Original Query, History, Date, Instructions) -> Call OpenAI API -> Get Response (in User's Language) -> Update History -> Send Response to Frontend -> Display

## Limitations & Future Improvements

- **Cross-Lingual RAG Performance:** While using multilingual models improves things, cross-lingual search/ranking might still occasionally be less precise than a fully monolingual pipeline.
- **In-Memory History:** Conversation history is lost when the backend restarts. Replace the simple dictionary with a database (Redis, PostgreSQL, etc.) for production persistence.
- **Translation API:** Query translation relies on MyMemory API, which has limits. Could be swapped for paid/other services if needed.
- **Scalability:** The current setup is suitable for demos/light use. Production requires proper deployment strategies (multiple workers, containers, potentially a dedicated vector database).
- **Context Window Limits:** Long conversations might exceed LLM token limits. Consider history summarization techniques.
- **Framework Adoption:** For more complex RAG features or easier pipeline management, explore LangChain or LlamaIndex.
