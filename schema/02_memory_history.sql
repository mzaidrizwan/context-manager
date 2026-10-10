CREATE TABLE memory_history(
history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
context_id BIGINT NOT NULL REFERENCES context_memory(context_id) ON DELETE CASCADE,
operation VARCHAR(20) NOT NULL CHECK (operation IN ('created', 'updated', 'soft_deleted', 'restored')),
subject TEXT NOT NULL,
content TEXT NOT NULL,
memory_type VARCHAR(50) NOT NULL,
status VARCHAR(20) NOT NULL,
metadata JSONB NOT NULL DEFAULT '{}'::jsonb,changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);