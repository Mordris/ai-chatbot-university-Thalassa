
# Chatbot Project

This project consists of a **React frontend** and a **FastAPI backend**. The React frontend is responsible for handling the user interface (UI), while the FastAPI backend handles API requests, manages a FAISS search index, and generates AI-powered responses using the Mistral-7B model.

## Project Structure

### Frontend (React)

- **`public/`**: Contains static assets like favicons and logos.
  - `favicon.ico`: Favicon for the app.
  
- **`src/`**: Source code for the React app.
  - **`components/`**: Reusable UI components.
    - `ChatWindow.jsx`: Main chat UI.
    - `Message.jsx`: Individual chat messages (user/bot).
    - `TypingIndicator.jsx`: Displays "Writing..." animation.
    - `Header.jsx`: App header.
    - `WelcomeModal.jsx`: Initial user warning modal.
    
  - **`hooks/`**: Custom React hooks.
    - `useChat.js`: Manages chat logic, state, and API calls.
    
  - **`styles/`**: Styling for the app.
    - `global.css`: Global styles.
    - `theme.js`: Custom theme file (e.g., colors, fonts).
    
  - **`utils/`**: Utility functions.
    - `api.js`: API request functions for backend communication.
    
  - **`App.jsx`**: Main entry point for the app.
  - **`index.js`**: Renders the React app.

- **`package.json`**: Project metadata, dependencies, and scripts.
- **`.gitignore`**: Specifies files/folders to be ignored by Git.
- **`README.md`**: Project documentation (this file).

### Backend (FastAPI)

- **`app/`**: Backend logic for FastAPI server.
  - `main.py`: FastAPI server file with API route definitions.
  - `faiss_search.py`: FAISS search utility for efficient document retrieval.
  - `ai_response.py`: Mistral-7B AI response generator.
  - `config.py`: Configuration file (e.g., API keys, paths).
  - `requirements.txt`: Python dependencies for the backend.

- **`data/`**: Data used for the backend.
  - `faiss_index.bin`: FAISS index file for fast search.
  - `metadata.npy`: Metadata for indexed chunks.

- **`extracted_texts/`**: Folder containing extracted text files for indexing.

- **`README.md`**: Backend documentation.
- **`.env`**: Environment variables for sensitive info (e.g., API keys, credentials).
- **`run.sh`**: Shell script to start the FastAPI server.

## Setup Instructions

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install the required dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open `http://localhost:3000` in your browser to view the frontend.

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scriptsctivate
   ```

3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. The backend will be available at `http://localhost:8000`.

### Environment Variables

The backend requires certain environment variables to run. Create a `.env` file in the `backend` directory with the following variables:

```bash
FAISS_INDEX_PATH=/path/to/faiss_index.bin
AI_API_KEY=your_ai_api_key
```

## Usage

1. Start the frontend and backend as described in the setup instructions.
2. Navigate to the frontend URL (`http://localhost:3000`).
3. Interact with the chatbot UI, which will send requests to the FastAPI backend.
4. The backend uses FAISS to search for relevant information and the Mistral-7B model to generate AI responses.

## License

This project is licensed under the MIT License.
