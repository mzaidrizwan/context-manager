CREATE TABLE context_memory(
context_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
subject TEXT NOT NULL,
content TEXT NOT NULL,
memory_type VARCHAR(50) NOT NULL CHECK (memory_type IN('fact', 'preference', 'instruction', 'constraint', 'goal', 'other')),
status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN('active', 'superseded', 'expired', 'deleted')),
confidence NUMERIC(3,2) CHEC
);