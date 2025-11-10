-- Agentic Sandbox System Database Schema
-- PostgreSQL 15+ with PGVector extension

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search optimization
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- For encryption

-- ===================================================================
-- AGENTS TABLE
-- Stores agent configurations and metadata
-- ===================================================================
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('chat', 'task_planner')),
    api_provider VARCHAR(50) NOT NULL CHECK (api_provider IN ('openai', 'anthropic')),
    model VARCHAR(100) NOT NULL,
    system_prompt TEXT,
    config_json JSONB,  -- Full JSON config for flexibility
    api_key_encrypted TEXT,  -- Encrypted API key
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'error')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for agents table
CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(type);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at DESC);

-- ===================================================================
-- CONVERSATIONS TABLE
-- Stores chat interaction logs
-- ===================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    rag_context JSONB,  -- Retrieved documents used in response
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for conversations table
CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(agent_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_agent_timestamp ON conversations(agent_id, timestamp DESC);

-- ===================================================================
-- KNOWLEDGE_VECTORS TABLE
-- Stores RAG embeddings with PGVector
-- ===================================================================
CREATE TABLE IF NOT EXISTS knowledge_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- OpenAI text-embedding-3-small dimension
    metadata JSONB,  -- Source file, page number, chunk index, etc.
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for knowledge_vectors table
CREATE INDEX IF NOT EXISTS idx_vectors_agent ON knowledge_vectors(agent_id);

-- IVFFlat index for fast cosine similarity search
-- Note: Adjust 'lists' parameter based on dataset size
-- Rule of thumb: lists = sqrt(total_rows)
-- For <10K rows: lists=100, 10K-100K: lists=1000, >100K: lists=2000
CREATE INDEX IF NOT EXISTS idx_vectors_embedding ON knowledge_vectors
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternative: HNSW index (more accurate but slower to build)
-- CREATE INDEX idx_vectors_embedding_hnsw ON knowledge_vectors
-- USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 64);

-- ===================================================================
-- AUDIT_LOGS TABLE
-- Tracks system events and changes
-- ===================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    user_id VARCHAR(255),  -- Future: multi-user support
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for audit_logs table
CREATE INDEX IF NOT EXISTS idx_audit_agent ON audit_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC);

-- ===================================================================
-- API_USAGE TABLE
-- Tracks token consumption and costs
-- ===================================================================
CREATE TABLE IF NOT EXISTS api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    api_provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    tokens_used INTEGER NOT NULL,
    cost_usd VARCHAR(20),  -- Estimated cost in USD
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for api_usage table
CREATE INDEX IF NOT EXISTS idx_usage_agent ON api_usage(agent_id);
CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON api_usage(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_usage_agent_timestamp ON api_usage(agent_id, timestamp DESC);

-- ===================================================================
-- TRIGGERS
-- Auto-update timestamps and maintain data integrity
-- ===================================================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for agents table
DROP TRIGGER IF EXISTS update_agents_updated_at ON agents;
CREATE TRIGGER update_agents_updated_at
BEFORE UPDATE ON agents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- UTILITY FUNCTIONS
-- Helper functions for common operations
-- ===================================================================

-- Function to search vectors with cosine similarity
CREATE OR REPLACE FUNCTION search_similar_vectors(
    query_embedding vector(1536),
    target_agent_id UUID,
    result_limit INTEGER DEFAULT 3
)
RETURNS TABLE (
    chunk_text TEXT,
    distance FLOAT,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        kv.chunk_text,
        (kv.embedding <-> query_embedding)::FLOAT AS distance,
        kv.metadata
    FROM knowledge_vectors kv
    WHERE kv.agent_id = target_agent_id
    ORDER BY distance
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get agent statistics
CREATE OR REPLACE FUNCTION get_agent_stats(target_agent_id UUID)
RETURNS TABLE (
    conversation_count BIGINT,
    total_tokens BIGINT,
    total_cost NUMERIC,
    avg_response_time_ms FLOAT,
    knowledge_base_size BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM conversations WHERE agent_id = target_agent_id) AS conversation_count,
        (SELECT COALESCE(SUM(tokens_used), 0) FROM api_usage WHERE agent_id = target_agent_id) AS total_tokens,
        (SELECT COALESCE(SUM(cost_usd::NUMERIC), 0) FROM api_usage WHERE agent_id = target_agent_id) AS total_cost,
        (SELECT COALESCE(AVG(response_time_ms), 0) FROM conversations WHERE agent_id = target_agent_id) AS avg_response_time_ms,
        (SELECT COUNT(*) FROM knowledge_vectors WHERE agent_id = target_agent_id) AS knowledge_base_size;
END;
$$ LANGUAGE plpgsql;

-- ===================================================================
-- VIEWS
-- Convenient views for common queries
-- ===================================================================

-- View: Agent summary with metrics
CREATE OR REPLACE VIEW agent_summary AS
SELECT
    a.id,
    a.name,
    a.type,
    a.api_provider,
    a.model,
    a.status,
    a.created_at,
    COUNT(DISTINCT c.id) AS conversation_count,
    COALESCE(SUM(u.tokens_used), 0) AS total_tokens_used,
    COALESCE(SUM(u.cost_usd::NUMERIC), 0) AS total_cost_usd,
    COUNT(DISTINCT kv.id) AS knowledge_base_chunks
FROM agents a
LEFT JOIN conversations c ON a.id = c.agent_id
LEFT JOIN api_usage u ON a.id = u.agent_id
LEFT JOIN knowledge_vectors kv ON a.id = kv.agent_id
GROUP BY a.id;

-- View: Recent conversations with agent info
CREATE OR REPLACE VIEW recent_conversations AS
SELECT
    c.id,
    c.agent_id,
    a.name AS agent_name,
    c.user_message,
    c.agent_response,
    c.tokens_used,
    c.response_time_ms,
    c.timestamp
FROM conversations c
JOIN agents a ON c.agent_id = a.id
ORDER BY c.timestamp DESC;

-- ===================================================================
-- INITIAL DATA (Optional)
-- Sample data for testing
-- ===================================================================

-- Uncomment to insert sample agent
-- INSERT INTO agents (name, type, api_provider, model, system_prompt, status)
-- VALUES (
--     'Sample Support Bot',
--     'chat',
--     'openai',
--     'gpt-4',
--     'You are a friendly customer support agent for an online store.',
--     'active'
-- );

-- ===================================================================
-- PERMISSIONS (Adjust as needed)
-- ===================================================================

-- Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO agentuser;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO agentuser;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO agentuser;

-- ===================================================================
-- CLEANUP FUNCTIONS
-- Useful for maintenance
-- ===================================================================

-- Function to delete old conversations (data retention)
CREATE OR REPLACE FUNCTION cleanup_old_conversations(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM conversations
    WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ===================================================================
-- PERFORMANCE TIPS
-- ===================================================================

-- 1. Vacuum regularly to maintain index performance
-- VACUUM ANALYZE knowledge_vectors;

-- 2. Monitor vector search performance
-- EXPLAIN ANALYZE SELECT * FROM knowledge_vectors ORDER BY embedding <-> '[...]'::vector LIMIT 3;

-- 3. Adjust IVFFlat lists parameter if dataset grows
-- DROP INDEX idx_vectors_embedding;
-- CREATE INDEX idx_vectors_embedding ON knowledge_vectors USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1000);

-- 4. For very large datasets, consider partitioning by agent_id
-- CREATE TABLE conversations_partitioned (LIKE conversations INCLUDING ALL) PARTITION BY HASH (agent_id);

COMMENT ON TABLE agents IS 'Stores AI agent configurations and metadata';
COMMENT ON TABLE conversations IS 'Logs of chat interactions between users and agents';
COMMENT ON TABLE knowledge_vectors IS 'Vector embeddings for RAG (Retrieval-Augmented Generation)';
COMMENT ON TABLE audit_logs IS 'System event logs for auditing and debugging';
COMMENT ON TABLE api_usage IS 'Tracks API token consumption and costs';
