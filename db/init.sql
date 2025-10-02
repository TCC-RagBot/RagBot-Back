CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; 

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE message_source_chunks (
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    chunk_content TEXT NOT NULL,
    document_name TEXT NOT NULL,
    similarity_score FLOAT,
    PRIMARY KEY (message_id, chunk_content)
);