# Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [RAG Implementation](#rag-implementation)
5. [Database Design](#database-design)
6. [API Design](#api-design)
7. [Security Considerations](#security-considerations)
8. [Scalability & Performance](#scalability--performance)
9. [Deployment Architecture](#deployment-architecture)

---

## System Overview

The Agentic Sandbox System is a microservices-based platform designed to democratize AI agent development. It abstracts the complexity of agent creation, RAG implementation, and API integration behind an intuitive interface while maintaining production-grade architecture.

### Design Principles

1. **Modularity**: Each component (frontend, backend, database) is independently deployable
2. **Portability**: Docker containerization ensures consistent behavior across environments
3. **Simplicity**: JSON-based configuration for human readability
4. **Extensibility**: Plugin architecture for future agent types and API providers
5. **Auditability**: Comprehensive logging and data persistence

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│                     (http://localhost:3000)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend Container                          │
│                      (React + Nginx)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Agent Form   │  │  Chat Page   │  │  Audit Logs  │         │
│  │  Component   │  │  Component   │  │  Component   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│           │                │                 │                   │
│           └────────────────┴─────────────────┘                   │
│                      API Client Service                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API (:8000)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend Container                            │
│                   (FastAPI + Python 3.11)                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    API Layer                               │ │
│  │  /agents/create  │  /agents/chat  │  /rag/upload          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                             │                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  Service Layer                             │ │
│  │  AgentManager │ RAGPipeline │ ConversationLogger          │ │
│  └───────────────────────────────────────────────────────────┘ │
│           │                │                 │                   │
│           ├────────────────┼─────────────────┤                   │
│           ▼                ▼                 ▼                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐        │
│  │   OpenAI    │  │  Anthropic   │  │  Config Store  │        │
│  │     SDK     │  │     SDK      │  │   (JSON Files) │        │
│  └─────────────┘  └──────────────┘  └────────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ PostgreSQL Protocol (:5432)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database Container                            │
│                 (PostgreSQL 15 + PGVector)                       │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐       │
│  │    agents    │  │ conversations  │  │   vectors    │       │
│  │    table     │  │     table      │  │    table     │       │
│  └──────────────┘  └────────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌────────────────┐                          │
│  │ audit_logs   │  │   api_usage    │                          │
│  │    table     │  │     table      │                          │
│  └──────────────┘  └────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘

External Services:
┌─────────────┐  ┌──────────────┐
│   OpenAI    │  │  Anthropic   │
│     API     │  │     API      │
└─────────────┘  └──────────────┘
```

---

## Component Architecture

### 1. Frontend (React Application)

**Technology Stack**:
- React 18+ (functional components with hooks)
- Axios for HTTP requests
- TailwindCSS for styling
- React Router for navigation
- Context API for state management

**Component Hierarchy**:

```
App.js
├── Router
│   ├── HomePage
│   │   └── AgentList
│   │       └── AgentCard
│   ├── CreateAgentPage
│   │   ├── AgentForm
│   │   │   ├── APISelector
│   │   │   ├── PromptEditor
│   │   │   └── KnowledgeBaseUploader
│   │   └── TemplateSelector
│   ├── AgentPage
│   │   ├── ChatInterface
│   │   │   ├── MessageList
│   │   │   │   └── Message
│   │   │   └── InputBox
│   │   ├── MetricsPanel
│   │   └── ConfigEditor
│   └── AuditLogsPage
│       ├── LogFilter
│       ├── LogTable
│       └── ExportButton
└── Context Providers
    ├── AuthContext
    ├── AgentContext
    └── NotificationContext
```

**Key Components**:

1. **AgentForm** (`src/components/AgentForm.js`)
   - Purpose: Create and edit agent configurations
   - State: Agent name, API selection, prompt, knowledge base
   - Validation: API key format, prompt length, file size
   - API calls: `POST /agents/create`, `PUT /agents/{id}`

2. **ChatInterface** (`src/components/ChatInterface.js`)
   - Purpose: Real-time agent interaction
   - State: Messages array, input text, loading state
   - Features: Auto-scroll, typing indicators, error handling
   - API calls: `POST /agents/{id}/chat`

3. **AuditLogViewer** (`src/components/AuditLogViewer.js`)
   - Purpose: Display conversation history and metrics
   - State: Logs array, filters (date, agent), pagination
   - Features: Search, export to JSON, date range filtering
   - API calls: `GET /audit/logs`, `GET /audit/export`

**State Management**:

```javascript
// AgentContext.js - Global agent state
{
  agents: [
    {
      id: "chat_001",
      name: "Customer Support Bot",
      type: "chat",
      api: "openai",
      model: "gpt-4",
      status: "active"
    }
  ],
  currentAgent: null,
  loading: false,
  error: null
}
```

### 2. Backend (FastAPI Application)

**Technology Stack**:
- FastAPI 0.100+ (async support)
- Pydantic for data validation
- SQLAlchemy 2.0+ for ORM
- OpenAI Python SDK 1.0+
- Anthropic Python SDK 0.18+
- PGVector for vector operations
- PyMuPDF, python-docx for text extraction

**Directory Structure**:

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── agents.py           # Agent CRUD endpoints
│   │   ├── chat.py             # Chat interaction endpoints
│   │   ├── rag.py              # RAG pipeline endpoints
│   │   └── audit.py            # Audit log endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agent.py            # Agent database model
│   │   ├── conversation.py     # Conversation model
│   │   ├── vector.py           # Vector storage model
│   │   └── audit.py            # Audit log model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── agent.py            # Agent Pydantic schemas
│   │   ├── chat.py             # Chat request/response schemas
│   │   └── rag.py              # RAG schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_manager.py    # Agent lifecycle management
│   │   ├── rag_pipeline.py     # RAG implementation
│   │   ├── llm_client.py       # OpenAI/Claude client
│   │   ├── vector_store.py     # PGVector operations
│   │   └── config_manager.py   # JSON config sync
│   └── utils/
│       ├── __init__.py
│       ├── text_extractor.py   # Document parsing
│       ├── chunking.py         # Text chunking
│       └── logger.py           # Logging utilities
├── requirements.txt
└── Dockerfile
```

**Service Layer Architecture**:

1. **AgentManager** (`services/agent_manager.py`)
   ```python
   class AgentManager:
       async def create_agent(config: AgentConfig) -> Agent
       async def get_agent(agent_id: str) -> Agent
       async def update_agent(agent_id: str, updates: dict) -> Agent
       async def delete_agent(agent_id: str) -> bool
       async def list_agents() -> List[Agent]
   ```

2. **RAGPipeline** (`services/rag_pipeline.py`)
   ```python
   class RAGPipeline:
       async def process_document(file: UploadFile, agent_id: str) -> bool
       async def retrieve_context(query: str, agent_id: str, top_k: int = 3) -> List[str]
       async def embed_text(text: str) -> List[float]
       async def search_vectors(query_vector: List[float], agent_id: str) -> List[Document]
   ```

3. **LLMClient** (`services/llm_client.py`)
   ```python
   class LLMClient:
       async def chat_completion(messages: List[dict], model: str, api: str) -> ChatResponse
       async def stream_completion(messages: List[dict]) -> AsyncIterator[str]
       def get_token_count(text: str) -> int
   ```

**API Endpoints**:

```
POST   /agents/create           Create new agent
GET    /agents                  List all agents
GET    /agents/{id}             Get agent details
PUT    /agents/{id}             Update agent config
DELETE /agents/{id}             Delete agent

POST   /agents/{id}/chat        Send message to agent
GET    /agents/{id}/status      Get agent status

POST   /rag/upload              Upload knowledge base
GET    /rag/documents/{agent_id} List knowledge base files
DELETE /rag/documents/{doc_id}  Delete document

GET    /audit/logs              Get conversation logs
GET    /audit/usage             Get API usage metrics
GET    /audit/export            Export logs as JSON

GET    /health                  Health check endpoint
```

### 3. Database (PostgreSQL + PGVector)

**Schema Design**: See [Database Design](#database-design) section below.

**Extensions**:
- `pgvector`: Vector similarity search
- `uuid-ossp`: UUID generation
- `pg_trgm`: Text search optimization

---

## Data Flow

### Agent Creation Flow

```
┌──────┐                                                          ┌──────────┐
│ User │                                                          │ Database │
└───┬──┘                                                          └────┬─────┘
    │                                                                  │
    │ 1. Fill agent form                                              │
    │    (name, API, prompt, knowledge base)                          │
    ├────────────────────────────────────────────┐                   │
    │                                             ▼                   │
    │                                      ┌─────────────┐            │
    │                                      │  Frontend   │            │
    │                                      └──────┬──────┘            │
    │                                             │                   │
    │                                             │ 2. POST /agents/create
    │                                             │    {name, api, prompt, file}
    │                                             ▼                   │
    │                                      ┌─────────────┐            │
    │                                      │   Backend   │            │
    │                                      └──────┬──────┘            │
    │                                             │                   │
    │                                             │ 3. Validate input │
    │                                             │    Generate agent_id
    │                                             │                   │
    │                                             │ 4. Save to JSON   │
    │                                             │    /configs/agent_001.json
    │                                             ▼                   │
    │                                      ┌─────────────┐            │
    │                                      │ Config File │            │
    │                                      └─────────────┘            │
    │                                             │                   │
    │                                             │ 5. INSERT agent   │
    │                                             ├──────────────────►│
    │                                             │                   │
    │                                             │ 6. Process file   │
    │                                             │    - Extract text │
    │                                             │    - Chunk text   │
    │                                             │    - Embed chunks │
    │                                             │                   │
    │                                             │ 7. INSERT vectors │
    │                                             ├──────────────────►│
    │                                             │                   │
    │                                             │ 8. Agent created  │
    │                                             │◄──────────────────┤
    │ 9. Redirect to chat page                   │                   │
    │◄───────────────────────────────────────────┤                   │
    │                                                                 │
```

### Chat Interaction Flow

```
┌──────┐                                                          ┌──────────┐
│ User │                                                          │ Database │
└───┬──┘                                                          └────┬─────┘
    │                                                                  │
    │ 1. Type message: "What's your return policy?"                  │
    ├────────────────────────────────────────────┐                   │
    │                                             ▼                   │
    │                                      ┌─────────────┐            │
    │                                      │  Frontend   │            │
    │                                      └──────┬──────┘            │
    │                                             │                   │
    │                                             │ 2. POST /agents/{id}/chat
    │                                             │    {message: "What's..."}
    │                                             ▼                   │
    │                                      ┌─────────────┐            │
    │                                      │   Backend   │            │
    │                                      └──────┬──────┘            │
    │                                             │                   │
    │                                             │ 3. Load agent config
    │                                             │◄──────────────────┤
    │                                             │                   │
    │                                             │ 4. Embed query    │
    │                                             │    "What's..." → vector
    │                                             │                   │
    │                                             │ 5. Search similar vectors
    │                                             ├──────────────────►│
    │                                             │                   │
    │                                             │ 6. Return top-3 chunks
    │                                             │◄──────────────────┤
    │                                             │    ["Q: return policy...",
    │                                             │     "...30 days...",
    │                                             │     "...original condition..."]
    │                                             │                   │
    │                                             │ 7. Build prompt   │
    │                                             │    System: "You are..."
    │                                             │    Context: [chunks]
    │                                             │    User: "What's..."
    │                                             │                   │
    │                                             │ 8. Call OpenAI/Claude
    │                                             ├──────────────────►│
    │                                             │                 External
    │                                             │                   API
    │                                             │ 9. Get response   │
    │                                             │◄──────────────────┤
    │                                             │    "We accept returns..."
    │                                             │                   │
    │                                             │ 10. Log conversation
    │                                             ├──────────────────►│
    │                                             │     INSERT into conversations
    │                                             │                   │
    │ 11. Display response                       │                   │
    │    "We accept returns within 30 days..."   │                   │
    │◄───────────────────────────────────────────┤                   │
    │                                                                 │
```

### Configuration Sync Flow

The system maintains dual persistence: JSON files for human readability and Postgres for querying.

```
┌─────────────┐                  ┌──────────────┐
│  JSON File  │◄────────────────►│   Postgres   │
│  (Primary)  │   Bidirectional  │  (Secondary) │
└─────────────┘      Sync        └──────────────┘

On Create/Update:
1. Validate input
2. Write to JSON file (source of truth)
3. Parse JSON
4. Upsert to Postgres
5. Confirm sync

On Read:
1. Read from Postgres (fast querying)
2. If missing, fallback to JSON
3. Sync to Postgres if discrepancy
```

---

## RAG Implementation

### Overview

The RAG (Retrieval-Augmented Generation) pipeline enhances agent responses by retrieving relevant information from uploaded knowledge bases before generating answers.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAG Pipeline                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐              │
│  │   Ingest   │──►│  Process   │──►│   Store    │              │
│  │  Document  │   │  Document  │   │  Vectors   │              │
│  └────────────┘   └────────────┘   └────────────┘              │
│        │                 │                 │                     │
│        ▼                 ▼                 ▼                     │
│  Upload file      Extract text      Embed chunks                │
│  (PDF/TXT/       Chunk text         Store in PGVector           │
│   DOCX/JSON)     (500 chars)        (1536 dimensions)           │
│                                                                  │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐              │
│  │   Query    │──►│  Retrieve  │──►│  Augment   │              │
│  │  Embedding │   │  Context   │   │  Prompt    │              │
│  └────────────┘   └────────────┘   └────────────┘              │
│        │                 │                 │                     │
│        ▼                 ▼                 ▼                     │
│  Embed query      Search vectors    Build final prompt          │
│  (user message)   (cosine similarity) Add retrieved docs        │
│                   Return top-K       Send to LLM                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Text Extraction

**Supported Formats**:

| Format | Library        | Extraction Method                    |
|--------|----------------|--------------------------------------|
| TXT    | Built-in       | Direct file read                     |
| JSON   | Built-in       | Parse and extract text fields        |
| PDF    | PyMuPDF        | Page-by-page text extraction         |
| DOCX   | python-docx    | Paragraph-by-paragraph extraction    |

**Implementation** (`utils/text_extractor.py`):

```python
class TextExtractor:
    def extract(self, file_path: str, file_type: str) -> str:
        """Extract text from various file formats."""

        if file_type == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif file_type == "json":
            with open(file_path, 'r') as f:
                data = json.load(f)
                return self._extract_text_from_json(data)

        elif file_type == "pdf":
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text

        elif file_type == "docx":
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
```

### Text Chunking

**Strategy**: Fixed-size chunks with overlap

**Parameters**:
- **Chunk Size**: 500 characters
- **Overlap**: 50 characters (10%)
- **Separator**: Sentence boundaries (. ! ?)

**Why Overlap?**
Prevents splitting related information across chunks, improving retrieval accuracy.

**Implementation** (`utils/chunking.py`):

```python
class TextChunker:
    def chunk(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Find sentence boundary
            if end < len(text):
                for sep in ['. ', '! ', '? ', '\n']:
                    boundary = text.rfind(sep, start, end)
                    if boundary != -1:
                        end = boundary + 1
                        break

            chunks.append(text[start:end].strip())
            start = end - overlap

        return chunks
```

### Vector Embedding

**Model**: OpenAI `text-embedding-3-small`

**Specifications**:
- **Dimensions**: 1536
- **Max Input**: 8191 tokens
- **Cost**: $0.02 / 1M tokens (as of 2025)
- **Performance**: ~1000 chunks/minute

**Implementation** (`services/rag_pipeline.py`):

```python
class RAGPipeline:
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for text."""

        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            encoding_format="float"
        )

        return response.data[0].embedding  # 1536-dimensional vector
```

### Vector Storage (PGVector)

**Extension Setup**:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Table Schema**:

```sql
CREATE TABLE knowledge_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- PGVector type
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX ON agent_id,
    INDEX USING ivfflat (embedding vector_cosine_ops)  -- Fast similarity search
);
```

**Index Type**: IVFFlat (Inverted File with Flat compression)
- **Purpose**: Accelerates cosine similarity search
- **Performance**: ~10x faster than brute-force on 10K+ vectors

### Semantic Search

**Similarity Metric**: Cosine Distance

**Formula**:
```
distance = 1 - (A · B) / (||A|| * ||B||)
```
- Range: [0, 2] (0 = identical, 2 = opposite)
- Lower distance = higher similarity

**Query Implementation**:

```python
async def search_vectors(
    self,
    query_vector: List[float],
    agent_id: str,
    top_k: int = 3
) -> List[Document]:
    """Search for similar vectors using PGVector."""

    query = """
        SELECT
            chunk_text,
            embedding <-> $1::vector AS distance,
            metadata
        FROM knowledge_vectors
        WHERE agent_id = $2
        ORDER BY distance
        LIMIT $3;
    """

    results = await self.db.fetch(
        query,
        query_vector,
        agent_id,
        top_k
    )

    return [
        Document(
            text=row['chunk_text'],
            distance=row['distance'],
            metadata=row['metadata']
        )
        for row in results
    ]
```

**Optimization**:
- **IVFFlat Index**: Reduces search time from O(n) to O(log n)
- **Agent Filtering**: `WHERE agent_id = ...` narrows search space
- **Top-K Limiting**: Retrieves only most relevant results

### Prompt Augmentation

**Template**:

```python
def build_augmented_prompt(
    system_prompt: str,
    user_message: str,
    context_docs: List[str]
) -> List[dict]:
    """Build prompt with RAG context."""

    context = "\n\n".join([
        f"[Document {i+1}]\n{doc}"
        for i, doc in enumerate(context_docs)
    ])

    messages = [
        {
            "role": "system",
            "content": f"{system_prompt}\n\nUse the following context to answer questions accurately:\n\n{context}"
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    return messages
```

**Example**:

```
System Prompt:
  You are a friendly customer support agent.

  Use the following context to answer questions accurately:

  [Document 1]
  Q: What is your return policy?
  A: We accept returns within 30 days of purchase.

  [Document 2]
  Items must be in original condition with tags attached.

  [Document 3]
  Refunds are processed within 5-7 business days.

User Message:
  What's your return policy?
```

### Performance Characteristics

| Operation              | Latency (Avg) | Notes                          |
|------------------------|---------------|--------------------------------|
| Text Extraction (1MB)  | 200ms         | PDF slowest, TXT fastest       |
| Chunking (10K chars)   | 50ms          | Linear time complexity         |
| Embedding (500 chars)  | 100ms         | Network call to OpenAI         |
| Vector Insert (1 chunk)| 10ms          | Postgres write                 |
| Vector Search (top-3)  | 50ms          | With IVFFlat index             |
| **Total RAG Pipeline** | **~400ms**    | For single query               |

**Optimization Tips**:
1. **Batch Embedding**: Embed multiple chunks in one API call (up to 2048 per request)
2. **Index Tuning**: Adjust IVFFlat `lists` parameter for dataset size
3. **Caching**: Cache embeddings for frequently accessed queries
4. **Async Processing**: Use async/await for parallel operations

---

## Database Design

### Entity-Relationship Diagram

```
┌─────────────────────┐
│      agents         │
├─────────────────────┤
│ id (PK)             │◄────────┐
│ name                │         │
│ type                │         │
│ api_provider        │         │
│ model               │         │
│ system_prompt       │         │
│ config_json         │         │
│ status              │         │
│ created_at          │         │
│ updated_at          │         │
└─────────────────────┘         │
                                │
                                │ 1:N
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ conversations   │   │ knowledge_vectors│   │   audit_logs    │
├─────────────────┤   ├──────────────────┤   ├─────────────────┤
│ id (PK)         │   │ id (PK)          │   │ id (PK)         │
│ agent_id (FK)   │   │ agent_id (FK)    │   │ agent_id (FK)   │
│ user_message    │   │ chunk_text       │   │ event_type      │
│ agent_response  │   │ embedding        │   │ event_data      │
│ tokens_used     │   │ metadata         │   │ user_id         │
│ response_time_ms│   │ created_at       │   │ timestamp       │
│ timestamp       │   └──────────────────┘   └─────────────────┘
└─────────────────┘

┌─────────────────┐
│   api_usage     │
├─────────────────┤
│ id (PK)         │
│ agent_id (FK)   │
│ api_provider    │
│ model           │
│ tokens_used     │
│ cost_usd        │
│ timestamp       │
└─────────────────┘
```

### Schema SQL

**Full Schema** (`database/schema.sql`):

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Agents table: Core agent configurations
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'chat', 'task_planner' (future)
    api_provider VARCHAR(50) NOT NULL,  -- 'openai', 'anthropic'
    model VARCHAR(100) NOT NULL,  -- 'gpt-4', 'claude-3-sonnet'
    system_prompt TEXT,
    config_json JSONB,  -- Full JSON config
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'inactive', 'error'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_agents_type (type),
    INDEX idx_agents_status (status)
);

-- Conversations table: Chat interaction logs
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    rag_context JSONB,  -- Retrieved documents used
    timestamp TIMESTAMP DEFAULT NOW(),

    INDEX idx_conversations_agent (agent_id),
    INDEX idx_conversations_timestamp (timestamp DESC)
);

-- Knowledge vectors table: RAG embeddings
CREATE TABLE knowledge_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- OpenAI embedding dimension
    metadata JSONB,  -- Source file, page number, etc.
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_vectors_agent (agent_id)
);

-- Create IVFFlat index for fast similarity search
CREATE INDEX idx_vectors_embedding ON knowledge_vectors
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- Tune based on dataset size

-- Audit logs table: System events
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'agent_created', 'config_updated', etc.
    event_data JSONB,
    user_id VARCHAR(255),  -- Future: multi-user support
    timestamp TIMESTAMP DEFAULT NOW(),

    INDEX idx_audit_agent (agent_id),
    INDEX idx_audit_type (event_type),
    INDEX idx_audit_timestamp (timestamp DESC)
);

-- API usage table: Cost tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    api_provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    tokens_used INTEGER NOT NULL,
    cost_usd DECIMAL(10, 6),  -- Estimated cost
    timestamp TIMESTAMP DEFAULT NOW(),

    INDEX idx_usage_agent (agent_id),
    INDEX idx_usage_timestamp (timestamp DESC)
);

-- Trigger: Update agents.updated_at on modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agents_updated_at
BEFORE UPDATE ON agents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

### Indexing Strategy

1. **Primary Keys**: UUIDs for global uniqueness
2. **Foreign Keys**: Indexed automatically by Postgres
3. **Timestamp Indexes**: DESC order for recent-first queries
4. **Vector Index**: IVFFlat for cosine similarity search
5. **Composite Indexes**: (agent_id, timestamp) for filtered time-series queries

---

## API Design

### RESTful Principles

- **Resource-Based URLs**: `/agents`, `/conversations`, `/rag`
- **HTTP Methods**: GET (read), POST (create), PUT (update), DELETE (delete)
- **Status Codes**: 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error)
- **JSON Payloads**: Request and response bodies in JSON

### Endpoint Specifications

#### Agent Management

**Create Agent**
```http
POST /agents/create
Content-Type: application/json

{
  "name": "Customer Support Bot",
  "type": "chat",
  "api_provider": "openai",
  "model": "gpt-4",
  "system_prompt": "You are a friendly support agent.",
  "api_key": "sk-..."
}

Response: 201 Created
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Customer Support Bot",
  "status": "active",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**List Agents**
```http
GET /agents?status=active&type=chat

Response: 200 OK
{
  "agents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Customer Support Bot",
      "type": "chat",
      "api_provider": "openai",
      "model": "gpt-4",
      "status": "active"
    }
  ],
  "total": 1
}
```

#### Chat Interaction

**Send Message**
```http
POST /agents/{agent_id}/chat
Content-Type: application/json

{
  "message": "What's your return policy?",
  "stream": false
}

Response: 200 OK
{
  "response": "We accept returns within 30 days of purchase...",
  "tokens_used": 45,
  "response_time_ms": 1230,
  "rag_context": [
    "Q: What is your return policy? A: We accept...",
    "...within 30 days of purchase..."
  ]
}
```

#### RAG Pipeline

**Upload Knowledge Base**
```http
POST /rag/upload
Content-Type: multipart/form-data

agent_id: 550e8400-e29b-41d4-a716-446655440000
file: [faq.pdf]

Response: 201 Created
{
  "document_id": "doc_123",
  "chunks_created": 45,
  "status": "processed"
}
```

### Error Handling

**Standard Error Response**:
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid or expired.",
    "details": {
      "field": "api_key",
      "provided_value": "sk-invalid..."
    }
  }
}
```

**Error Codes**:
- `INVALID_INPUT`: Validation failure
- `AGENT_NOT_FOUND`: Agent ID doesn't exist
- `API_KEY_INVALID`: External API authentication failed
- `FILE_TOO_LARGE`: Knowledge base exceeds 1MB
- `RATE_LIMIT_EXCEEDED`: Too many requests

---

## Security Considerations

### API Key Management

1. **Storage**: Encrypted in Postgres using `pgcrypto`
   ```sql
   CREATE EXTENSION IF NOT EXISTS pgcrypto;

   -- Encrypt API keys
   INSERT INTO agents (api_key_encrypted)
   VALUES (pgp_sym_encrypt('sk-real-key', 'encryption-passphrase'));

   -- Decrypt when needed
   SELECT pgp_sym_decrypt(api_key_encrypted, 'encryption-passphrase');
   ```

2. **Environment Variables**: Encryption passphrase in `.env`
3. **No Logging**: API keys never logged or exposed in responses

### Authentication (Future)

1. **OAuth2**: Google, GitHub sign-in
2. **JWT Tokens**: Stateless session management
3. **Role-Based Access**: Admin, User roles

### Input Validation

1. **Pydantic Schemas**: Type checking and validation
2. **File Upload Limits**: Max 1MB, allowed extensions only
3. **SQL Injection Prevention**: Parameterized queries
4. **XSS Protection**: Sanitize user inputs in frontend

### Rate Limiting

1. **API Rate Limits**: 100 requests/minute per user
2. **Token Budgets**: Max 10K tokens/hour per agent
3. **Circuit Breaker**: Stop requests on repeated external API failures

---

## Scalability & Performance

### Current Limitations (MVP)

- **Max Agents**: 10 concurrent
- **Max Knowledge Base**: 1MB per agent
- **Max Vectors**: ~10K per agent (PGVector performant up to 1M)
- **Concurrent Users**: ~50 (single server)

### Horizontal Scaling (Future)

```
┌────────────┐      ┌────────────┐      ┌────────────┐
│  Frontend  │      │  Frontend  │      │  Frontend  │
│  Instance  │      │  Instance  │      │  Instance  │
└──────┬─────┘      └──────┬─────┘      └──────┬─────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Load Balancer│
                    └──────┬──────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────▼─────┐      ┌──────▼─────┐      ┌──────▼─────┐
│  Backend   │      │  Backend   │      │  Backend   │
│  Instance  │      │  Instance  │      │  Instance  │
└──────┬─────┘      └──────┬─────┘      └──────┬─────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Postgres   │
                    │   Primary   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Postgres   │
                    │   Replica   │
                    └─────────────┘
```

### Optimization Strategies

1. **Caching**: Redis for frequently accessed configs
2. **Connection Pooling**: Postgres connection reuse
3. **Async Processing**: Background jobs for RAG vectorization
4. **CDN**: Static frontend assets
5. **Vector Index Tuning**: Adjust IVFFlat parameters

---

## Deployment Architecture

### Docker-compose Services

```yaml
services:
  frontend:
    image: agentic-sandbox-frontend
    ports: ["3000:80"]
    depends_on: [backend]

  backend:
    image: agentic-sandbox-backend
    ports: ["8000:8000"]
    depends_on: [db]
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/agentsandbox
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  db:
    image: pgvector/pgvector:pg15
    ports: ["5432:5432"]
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### Production Deployment (AWS Example)

```
┌─────────────────────────────────────────────────────────┐
│                      AWS Cloud                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐                                         │
│  │ CloudFront │  (CDN for frontend)                     │
│  └──────┬─────┘                                         │
│         │                                                │
│  ┌──────▼─────┐                                         │
│  │     S3     │  (React build artifacts)                │
│  └────────────┘                                         │
│                                                          │
│  ┌────────────┐                                         │
│  │    ALB     │  (Application Load Balancer)            │
│  └──────┬─────┘                                         │
│         │                                                │
│  ┌──────▼─────────┐                                     │
│  │  ECS Fargate   │  (Backend containers)               │
│  │   Auto-scaling │                                     │
│  └──────┬─────────┘                                     │
│         │                                                │
│  ┌──────▼─────┐                                         │
│  │    RDS     │  (PostgreSQL with PGVector)             │
│  │  Multi-AZ  │                                         │
│  └────────────┘                                         │
│                                                          │
│  ┌────────────┐                                         │
│  │  Secrets   │  (API keys, DB credentials)             │
│  │  Manager   │                                         │
│  └────────────┘                                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Appendix

### Technology Choices Rationale

| Component    | Choice            | Rationale                                      |
|--------------|-------------------|------------------------------------------------|
| Frontend     | React             | Component reusability, large ecosystem         |
| Backend      | FastAPI           | Async support, auto-generated docs, Python ML  |
| Database     | Postgres+PGVector | Open-source, vector search, ACID compliance    |
| Embedding    | text-embedding-3  | Cost-effective, high quality, OpenAI ecosystem |
| Container    | Docker            | Portability, easy local development            |

### Future Enhancements

1. **Multi-Agent Orchestration**: Agents coordinating on complex tasks
2. **Advanced RAG**: Hybrid search (semantic + keyword), reranking
3. **Streaming Responses**: Real-time token-by-token display
4. **Voice Interface**: Speech-to-text integration
5. **Analytics Dashboard**: Usage patterns, A/B testing
6. **Custom Embeddings**: Support for Sentence-Transformers, Cohere

### Glossary

- **RAG**: Retrieval-Augmented Generation - enhancing LLMs with external knowledge
- **PGVector**: PostgreSQL extension for vector similarity search
- **Embedding**: Numerical representation of text (e.g., 1536-dimensional vector)
- **Cosine Similarity**: Measure of similarity between two vectors
- **IVFFlat**: Index type for approximate nearest neighbor search
- **Chunking**: Splitting text into smaller, manageable pieces
- **LLM**: Large Language Model (e.g., GPT-4, Claude)
