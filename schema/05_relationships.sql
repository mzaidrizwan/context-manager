CREATE TABLE memory_relationship(
relationship_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
source_context_id BIGINT NOT NULL REFERENCES context_memory(context_id) ON DELETE CASCADE,
target_context_id BIGINT NOT NULL REFERENCES context_memory(context_id) ON DELETE CASCADE,
relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN('related_to', 'supersedes', 'contradicts', 'supports', 'derived_from')),
metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT check_no_self_relationship CHECK (source_context_id <> target_context_id),
CONSTRAINT unique_relationship_pair UNIQUE (source_context_id, target_context_id,relationship_type)
);