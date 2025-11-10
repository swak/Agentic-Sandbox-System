# Agentic Sandbox System

## Overview

The **Agentic Sandbox System** is a Dockerized, API-driven platform that enables users with minimal AI knowledge to create, configure, and interact with AI agents through an intuitive web dashboard. The MVP focuses on a chat agent powered by external APIs (OpenAI, Claude) with RAG (Retrieval-Augmented Generation) capabilities for context-aware responses.

### Problem Solved

Non-technical users face significant barriers when experimenting with AI agents due to:
- Complex setup processes requiring coding expertise
- Infrastructure management challenges
- Lack of intuitive interfaces for rapid prototyping

This system abstracts the complexity, allowing users to:
- Prototype AI agents in under 10 minutes with no coding
- Modify agent behaviors (prompts, tone) through a visual interface
- Test interactions in real-time and audit usage
- Deploy production-ready AI solutions with a single command

### Key Features

- **Visual Dashboard**: Create and manage AI agents through a React-based web interface
- **RAG Pipeline**: Upload knowledge bases for context-aware responses
- **Multi-API Support**: Integrate OpenAI, Claude, or custom API endpoints
- **Real-time Testing**: Chat with agents and see responses instantly
- **Audit Logs**: Track conversations, configuration changes, and API usage
- **One-Command Deployment**: Docker-compose for instant setup
- **JSON Configuration**: Human-readable config files with database persistence

---

## Architecture

### Components

1. **Frontend (React)**
   - Agent creation and configuration forms
   - Live chat interface
   - Audit logs and metrics dashboard
   - Configuration editor

2. **Backend (FastAPI)**
   - RESTful API for agent management
   - RAG pipeline (text extraction, vectorization, retrieval)
   - Integration with external AI APIs (OpenAI, Claude)
   - Conversation logging and metrics

3. **Database (Postgres + PGVector)**
   - Agent configurations (synced with JSON files)
   - Conversation logs
   - RAG vectors for semantic search
   - Audit trails

4. **Docker Environment**
   - Containerized services for portability
   - Agent runtime isolation
   - Database with PGVector extension

### Tech Stack

- **Frontend**: React, Axios, TailwindCSS
- **Backend**: FastAPI, Python 3.11+, Uvicorn
- **Database**: PostgreSQL 15+, PGVector extension
- **AI APIs**: OpenAI SDK, Anthropic SDK
- **Embedding**: text-embedding-3-small (1536 dimensions)
- **Text Extraction**: PyMuPDF, python-docx
- **Containerization**: Docker, Docker-compose

### Data Flow

```
[User] → [Dashboard] → [FastAPI API]
                           ↓
         ┌─────────────────┼─────────────────┐
         ↓                 ↓                 ↓
   [JSON Configs]    [Postgres/PGVector]  [AI APIs]
                           ↓
                    [Agent Runtime]
```

1. User creates agent via dashboard form (API key, prompt, knowledge base)
2. API saves configuration to JSON file and Postgres
3. Knowledge base is vectorized and stored in PGVector
4. Agent is initialized with configuration
5. User chats via dashboard; queries are augmented with RAG context
6. Responses logged to Postgres; metrics displayed in real-time

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.

---

## Setup Instructions

> **Windows Users**: See [SETUP_WINDOWS.md](SETUP_WINDOWS.md) for detailed Windows-specific instructions with Docker commands.

### Prerequisites

- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
  - **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - **Mac**: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)
- **Docker-compose**: Version 2.0+ (included with Docker Desktop)
- **API Keys**: OpenAI or Claude API key ([OpenAI](https://platform.openai.com/api-keys) | [Claude](https://console.anthropic.com/))
- **System Requirements**: 4GB+ RAM, 10GB disk space

### Quick Start (Windows)

1. **Create `.env` file**:
   ```cmd
   copy .env.example .env
   notepad .env
   ```
   Add your API keys and save.

2. **Run setup script**:
   ```cmd
   setup.bat
   ```

3. **Access the dashboard**: http://localhost:3000

See [SETUP_WINDOWS.md](SETUP_WINDOWS.md) for troubleshooting and detailed commands.

### Quick Start (Mac/Linux)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/agentic-sandbox-system.git
   cd agentic-sandbox-system
   ```

2. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   # OpenAI API Key (required if using OpenAI)
   OPENAI_API_KEY=sk-your-openai-key-here

   # Anthropic API Key (required if using Claude)
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
   ```

3. **Run Setup Script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Access the Dashboard**

   Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

   The FastAPI backend will be available at:
   ```
   http://localhost:8000
   API Docs: http://localhost:8000/docs
   ```

### Manual Setup (All Platforms)

If you prefer manual Docker commands:

```bash
# Build and start all services
docker compose build
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps

# Stop services
docker compose down
```

### Verify Installation

1. **Check Services Status**
   ```bash
   docker-compose ps
   ```

   You should see:
   - `agentic-sandbox-frontend` (running)
   - `agentic-sandbox-backend` (running)
   - `agentic-sandbox-db` (running)

2. **Test API**
   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {"status": "healthy", "database": "connected"}
   ```

3. **Test Database**
   ```bash
   docker-compose exec db psql -U agentuser -d agentsandbox -c "SELECT 1;"
   ```

---

## Usage Guide

### Creating Your First Chat Agent

1. **Navigate to Dashboard**
   - Open `http://localhost:3000`
   - Click "Create New Agent"

2. **Configure Agent**
   - **Agent Name**: Enter a descriptive name (e.g., "Customer Support Bot")
   - **Agent Type**: Select "Chat Agent"
   - **API Provider**: Choose "OpenAI" or "Claude"
   - **API Key**: Enter your API key (or use the one from `.env`)
   - **Model**: Select model (e.g., "gpt-4", "claude-3-sonnet")
   - **System Prompt**: Enter instructions or choose a template:
     ```
     You are a friendly customer support agent for an online store.
     Help customers with orders, returns, and product questions.
     Be concise and professional.
     ```

3. **Upload Knowledge Base (Optional)**
   - Click "Upload Knowledge Base"
   - Select a file (TXT, JSON, PDF, or DOCX)
   - Maximum size: 1MB for MVP
   - Example content (FAQ.txt):
     ```
     Q: What is your return policy?
     A: We accept returns within 30 days of purchase.

     Q: How long does shipping take?
     A: Standard shipping takes 5-7 business days.
     ```

4. **Create Agent**
   - Click "Create Agent"
   - Wait for initialization (5-10 seconds)
   - You'll be redirected to the agent's chat page

### Testing the Agent

1. **Chat Interface**
   - Type your message in the input box
   - Press Enter or click "Send"
   - View the agent's response in real-time

2. **Example Conversation**
   ```
   You: Where is my order?
   Agent: I'd be happy to help you track your order! To locate it,
          I'll need your order number or the email address used for
          the purchase. Could you provide that information?

   You: What's your return policy?
   Agent: We accept returns within 30 days of purchase. Items must
          be in original condition with tags attached. Please contact
          our support team to initiate a return.
   ```

3. **Metrics Display**
   - **Response Time**: Latency for each response
   - **Tokens Used**: API token consumption
   - **RAG Context**: Documents retrieved (if knowledge base enabled)

### Managing Agent Configuration

1. **Edit Agent**
   - Click "Edit Configuration" on the agent page
   - Modify prompt, model, or API settings
   - Changes are saved to JSON and Postgres
   - Click "Save & Restart" to apply changes

2. **Update Knowledge Base**
   - Click "Manage Knowledge Base"
   - Upload new files or delete existing ones
   - System re-vectorizes content automatically

3. **Delete Agent**
   - Click "Delete Agent"
   - Confirm deletion
   - Agent configuration and logs are removed

### Viewing Audit Logs

1. **Conversation History**
   - Navigate to "Audit Logs" tab
   - View all conversations with timestamps
   - Filter by date range or search keywords

2. **Configuration Changes**
   - See history of prompt/model updates
   - Track who made changes (future: multi-user support)

3. **API Usage Metrics**
   - Total tokens consumed
   - Cost estimation (based on API pricing)
   - Response time analytics

4. **Export Data**
   - Click "Export JSON"
   - Download conversation logs and configs
   - Format:
     ```json
     {
       "agent_id": "chat_001",
       "conversations": [
         {
           "timestamp": "2025-01-15T10:30:00Z",
           "user_message": "What's your return policy?",
           "agent_response": "We accept returns within 30 days...",
           "tokens_used": 45,
           "response_time_ms": 1230
         }
       ]
     }
     ```

---

## RAG Pipeline Explanation

The Retrieval-Augmented Generation (RAG) pipeline enables agents to answer questions based on uploaded knowledge bases, providing accurate, context-aware responses.

### How RAG Works

#### 1. Text Extraction
When you upload a knowledge base file:

- **Supported Formats**: TXT, JSON, PDF, DOCX
- **Extraction Process**:
  - **TXT/JSON**: Direct text reading
  - **PDF**: PyMuPDF extracts text from each page
  - **DOCX**: python-docx extracts paragraphs
- **Chunking**: Text is split into 500-character chunks with 50-character overlap
- **Example**:
  ```python
  # Input: FAQ.txt (2000 characters)
  # Output: 4 chunks of ~500 characters each
  chunks = [
    "Q: What is your return policy? A: We accept...",
    "...returns within 30 days. Q: How long does...",
    "...shipping take? A: Standard shipping...",
    "...takes 5-7 business days. Q: Do you..."
  ]
  ```

#### 2. Vectorization
Each text chunk is converted to a numerical vector:

- **Embedding Model**: OpenAI's `text-embedding-3-small`
- **Vector Dimensions**: 1536
- **Process**:
  ```python
  # Chunk: "Q: What is your return policy? A: We accept..."
  # Vector: [0.023, -0.891, 0.445, ..., 0.112] (1536 values)
  ```
- **Storage**: Vectors stored in Postgres with PGVector extension
- **Database Table**:
  ```sql
  CREATE TABLE knowledge_vectors (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255),
    chunk_text TEXT,
    embedding vector(1536),
    metadata JSONB
  );
  ```

#### 3. Semantic Search
When a user asks a question:

- **Query Vectorization**: User's question is converted to a vector
  ```python
  query = "What's your return policy?"
  query_vector = embed("What's your return policy?")
  # Result: [0.019, -0.883, 0.451, ..., 0.109]
  ```

- **Similarity Search**: PGVector finds the most similar chunks
  ```sql
  SELECT chunk_text,
         embedding <-> $1::vector AS distance
  FROM knowledge_vectors
  WHERE agent_id = 'chat_001'
  ORDER BY distance
  LIMIT 3;
  ```
  - `<->` operator calculates cosine distance
  - Lower distance = higher similarity
  - Returns top-3 most relevant chunks

- **Example Results**:
  ```
  1. "Q: What is your return policy? A: We accept..." (distance: 0.12)
  2. "...returns within 30 days of purchase..." (distance: 0.34)
  3. "...items must be in original condition..." (distance: 0.56)
  ```

#### 4. Context Augmentation
Retrieved chunks are added to the AI prompt:

- **Original Prompt**:
  ```
  You are a friendly customer support agent.
  ```

- **Augmented Prompt**:
  ```
  You are a friendly customer support agent.

  Use the following context to answer questions:

  Context:
  - Q: What is your return policy? A: We accept returns within 30 days...
  - ...returns within 30 days of purchase...
  - ...items must be in original condition...

  User Question: What's your return policy?
  ```

- **API Call**: Full prompt sent to OpenAI/Claude
- **Response**: Agent generates answer based on retrieved context

### RAG Performance

- **Retrieval Speed**: <500ms for small knowledge bases (<1MB)
- **Accuracy**: Significantly improved for domain-specific questions
- **Token Efficiency**: Only relevant context sent to API (reduces costs)
- **Scalability**: PGVector optimized for millions of vectors (future scaling)

### Example RAG Workflow

```
[User]: "How long does shipping take?"
          ↓
[Extract & Vectorize Query]
  Vector: [0.145, -0.678, ...]
          ↓
[PGVector Similarity Search]
  Top Result: "Q: How long does shipping take?
               A: Standard shipping takes 5-7 business days."
  Distance: 0.08 (very similar!)
          ↓
[Augment Prompt with Context]
  Prompt: "You are a support agent. Context: ...shipping takes 5-7 days...
           User: How long does shipping take?"
          ↓
[Send to OpenAI/Claude API]
          ↓
[Agent Response]: "Standard shipping takes 5-7 business days. We also offer
                   express shipping (2-3 days) for an additional fee."
          ↓
[Display to User + Log to Postgres]
```

### Best Practices for Knowledge Bases

1. **Structure Content Clearly**
   - Use Q&A format for FAQs
   - Break information into logical sections
   - Avoid extremely long paragraphs

2. **Optimize File Size**
   - MVP limit: 1MB per knowledge base
   - Remove redundant information
   - Use plain text when possible

3. **Test Retrieval**
   - Ask sample questions after uploading
   - Check if correct context is retrieved
   - Refine content if responses are inaccurate

4. **Update Regularly**
   - Re-upload updated knowledge bases
   - System automatically re-vectorizes content
   - Old vectors are replaced

---

## Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check Docker is running
   docker --version

   # Check ports are available (3000, 8000, 5432)
   netstat -an | grep -E '3000|8000|5432'

   # Restart services
   docker-compose down
   docker-compose up --build
   ```

2. **API key errors**
   - Verify keys in `.env` file
   - Check for extra spaces or quotes
   - Ensure keys are valid on provider's website

3. **Database connection errors**
   ```bash
   # Recreate database
   docker-compose down -v
   docker-compose up -d db
   docker-compose logs db
   ```

4. **Slow RAG responses**
   - Reduce knowledge base size
   - Check network connection to OpenAI/Claude
   - Increase Docker memory allocation

5. **Frontend not loading**
   ```bash
   # Rebuild frontend
   docker-compose up --build frontend

   # Check browser console for errors
   # Clear browser cache
   ```

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Access backend container
docker-compose exec backend /bin/bash

# Access database
docker-compose exec db psql -U agentuser -d agentsandbox
```

---

## Development

### Project Structure

```
agentic-sandbox-system/
├── frontend/                 # React dashboard
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API clients
│   │   └── App.js           # Main app
│   ├── package.json
│   └── Dockerfile
├── backend/                  # FastAPI server
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   └── main.py          # App entry point
│   ├── requirements.txt
│   └── Dockerfile
├── database/                 # Postgres setup
│   ├── schema.sql           # Database schema
│   └── init.sql             # Initialization
├── configs/                  # Sample configs
│   └── agent_config.json
├── docker-compose.yml
├── .env.example
├── setup.sh
├── README.md
└── ARCHITECTURE.md
```

### Running in Development Mode

```bash
# Backend (with hot reload)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (with hot reload)
cd frontend
npm install
npm start

# Database (Docker)
docker-compose up db
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/agentic-sandbox-system/issues)
- **Email**: shaun.wakashige@gmail.com

---

## Roadmap

### Current (MVP v1.0)
- ✅ Chat agent with OpenAI/Claude
- ✅ RAG pipeline with PGVector
- ✅ React dashboard
- ✅ Docker-compose deployment
- ✅ Audit logs and JSON export

### Future Enhancements
- 🔄 Multi-agent orchestration
- 🔄 Task planner agent type
- 🔄 Advanced analytics (sentiment analysis)
- 🔄 Multi-user authentication (OAuth2)
- 🔄 Cloud deployment templates (AWS, GCP)
- 🔄 Custom embedding models
- 🔄 Voice interface integration

---

**Built with ❤️ for AI enthusiasts and developers**
