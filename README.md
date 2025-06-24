# Autonomous AI Insight Engine

A mini autonomous LLM agent that processes research queries with context-aware, citation-backed responses.

## Features

- FastAPI endpoint for query processing
- Local vector store (FAISS) for document retrieval
- OpenAI LLM integration for answer generation
- Hallucination mitigation through strict context grounding
- Redis caching for identical queries 
- Streaming response support 
- SQLite query logging 

🚀 How to Run
Option 1: Local Setup
Prerequisites

    Python 3.9+

    Redis (for caching)
    bash

    # Install Redis (Mac/Linux)
    brew install redis       # Mac
    sudo apt install redis   # Ubuntu/Debian

    # Windows: Use WSL or Docker

1. Clone the Repository
bash

git clone https://github.com/maeme-23/Autonomous-AI-Insight-Engine.git
cd Autonomous-AI-Insight-Engine

2. Set Up Environment

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
.\venv\Scripts\activate       # Windows

3. Install Dependencies

    pip install -r requirements.txt

4. Configure Secrets

Create a .env file in the project root with your OpenAI API key:


   echo "OPENAI_API_KEY=your_api_key_here" > .env

    🔒 Never commit this file! It’s auto-ignored by .gitignore.

5. Run the API:
     uvicorn main:app --reload

#Access docs: http://localhost:8000/docs


🛠️ Environment Variables
Variable	Description	Example
OPENAI_API_KEY	OpenAI API key (required)	sk-abc123...
REDIS_URL	Redis connection URL	redis://redis:6379


🔒 Security Notes

    1. Always:

        Keep .env out of version control (verified by .gitignore).

        Rotate keys if accidentally exposed.

    2. For Production:

        Use GitHub Secrets (for CI/CD) or a vault service.

        Restrict API keys to specific IPs.


📂 Project Structure (Key Files)

├── .env                # Secrets (local only)
├── docker-compose.yml  # Docker setup
├── data/               # Sample documents
├── app/                # Core code
│   ├── main.py         # FastAPI app
│   └── ...             
└── README.md           # You are here :)
