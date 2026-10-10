CREATE TABLE source_record(
source_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('user_input', 'system', 'agent', 'document', 'external_api')),
identifier TEXT NOT NULL ,
metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory_source(
context_id BIGINT NOT NULL REFERENCES context_memory(context_id) ON DELETE CASCADE,
source_id BIGINT NOT NULL REFERENCES source_record(source_id) ON DELETE CASCADE,
attached_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (context_id, source_id)
);