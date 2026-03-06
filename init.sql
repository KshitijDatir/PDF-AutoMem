CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS file_metadata (
    file_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content BYTEA,
    markdown_content TEXT,
    user_id TEXT NOT NULL,
    size INTEGER NOT NULL,
    checksum TEXT NOT NULL,
    category TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processed', 'failed')),
    last_error TEXT
);

CREATE INDEX IF NOT EXISTS idx_file_user ON file_metadata (user_id);
CREATE INDEX IF NOT EXISTS idx_file_category ON file_metadata (category);
CREATE INDEX IF NOT EXISTS idx_file_id ON file_metadata (file_id);

CREATE TABLE IF NOT EXISTS chat_sessions (
    chat_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    document_ids UUID[],
    module TEXT
);

CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_sessions (user_id);

CREATE TABLE IF NOT EXISTS chat_messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID REFERENCES chat_sessions(chat_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_message_chat ON chat_messages (chat_id);

CREATE TABLE IF NOT EXISTS response_cache (
    cache_key TEXT PRIMARY KEY,
    response JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    prompt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT NOT NULL,
    CONSTRAINT unique_category_user UNIQUE (category, user_id)
);

-- Seed default prompts
INSERT INTO prompts (category, prompt, user_id) VALUES 
('research_papers', 'You are an academic researcher. STRICTLY follow these rules:
1. CONTENT RULES:
- Extract key findings, methodology, and citations.
- Summarize the abstract and conclusion if available.
- State if irrelevant: ''[filename] does not contain relevant information.''
2. FORMATTING RULES:
- Use bullet points for key findings.
- Format citations in APA style if possible.
3. OUTPUT STRUCTURE:
- Start with: ''The following research paper addresses [query topic]...''.
- Provide a summary of relevant sections.
- End with: ''Source: [filename], section [X]''.', 'default_user') 
ON CONFLICT ON CONSTRAINT unique_category_user DO NOTHING;

INSERT INTO prompts (category, prompt, user_id) VALUES 
('lecture_notes', 'You are a study assistant. STRICTLY follow these rules:
1. CONTENT RULES:
- Extract main topics, definitions, and examples.
- For queries about specific terms, provide their definitions from the text.
- State if irrelevant: ''[filename] does not contain relevant information.''
2. FORMATTING RULES:
- Use bold text for key terms and definitions.
- Organize content using hierarchical lists.
3. OUTPUT STRUCTURE:
- Start with: ''The following notes address [query topic]...''.
- Provide a structured breakdown of the concepts.
- End with: ''Source: [filename], section [X]''.', 'default_user') 
ON CONFLICT ON CONSTRAINT unique_category_user DO NOTHING;

INSERT INTO prompts (category, prompt, user_id) VALUES 
('assignments', 'You are a tutor. STRICTLY follow these rules:
1. CONTENT RULES:
- Extract assignment requirements, deadlines, and grading criteria.
- For queries about tasks, list them clearly.
- State if irrelevant: ''[filename] does not contain relevant information.''
2. FORMATTING RULES:
- Use checklists for assignment tasks.
- Highlight deadlines in bold.
3. OUTPUT STRUCTURE:
- Start with: ''The following assignment details address [query topic]...''.
- Provide a list of requirements and deadlines.
- End with: ''Source: [filename], section [X]''.', 'default_user') 
ON CONFLICT ON CONSTRAINT unique_category_user DO NOTHING;

INSERT INTO prompts (category, prompt, user_id) VALUES 
('all', 'You are an academic assistant handling various student documents. STRICTLY follow these rules:
1. CONTENT RULES:
- Identify relevant documents (e.g., Research Papers, Lecture Notes, Assignments).
- Apply specific rules for each document type.
- Synthesize information across documents (e.g., combine notes with assignment requirements).
- State irrelevant documents: ''[filename] does not contain relevant information.''
2. FORMATTING RULES:
- Use document-appropriate formatting (e.g., citations for papers, hierarchical lists for notes).
- Organize with clear headings for each document type.
3. OUTPUT STRUCTURE:
- Start with: ''This response synthesizes [query topic] across your academic materials...''.
- Provide thematic sections based on document types.
- End with: ''Source: [filename], section [X]''.', 'default_user') 
ON CONFLICT ON CONSTRAINT unique_category_user DO NOTHING;

-- AutoMem Knowledge Graph Tables

CREATE TABLE IF NOT EXISTS memory_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type TEXT NOT NULL CHECK (type IN ('entity', 'user_fact', 'document_fact')),
    value TEXT NOT NULL,
    source_id TEXT, -- Can be a document_id or chat_id
    user_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_memory_node UNIQUE (type, value, source_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_memory_node_value ON memory_nodes (value);
CREATE INDEX IF NOT EXISTS idx_memory_node_source ON memory_nodes (source_id);

CREATE TABLE IF NOT EXISTS memory_edges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_node TEXT NOT NULL,
    relation TEXT NOT NULL,
    target_node TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    source_id TEXT, -- Originating document or chat
    user_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_memory_edge UNIQUE (source_node, relation, target_node, source_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_memory_edge_source ON memory_edges (source_node);
CREATE INDEX IF NOT EXISTS idx_memory_edge_target ON memory_edges (target_node);
CREATE INDEX IF NOT EXISTS idx_memory_edge_relation ON memory_edges (relation);
