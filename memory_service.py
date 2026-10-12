import json
from database import get_connection

def create_memory(subject:str, content:str,memory_type:str,confidence:float=None,metadata:dict=None)-> dict:
    if not subject or not subject.strip():
        raise ValueError("Subject cant be empty")
    if not content or not content.strip():
        raise ValueError("content cant be empty")
    
    valid_types = {'fact','preference', 'instruction', 'constraint', 'goal', 'other'}
    if memory_type not in valid_types:
        raise ValueError(f"'{memory_type}' is invalid. Only '{valid_types} are acceptable'")
    if metadata is None:
        metadata={}
        
    # converting dict to json
    metadata_json = json.dumps(metadata)

    with get_connection() as conn:
        with conn.cursor() as cur:
            # inserting primary memory
            insert_memory_sql = """
            INSERT INTO context_memory(subject,content,memory_type,confidence,metadata) VALUES (%s,%s,%s,%s,%s) RETURNING context_id,subject,content,memory_type,status,confidence,metadata,created_at,updated_at;
            """

            cur.execute(
                insert_memory_sql,(subject.strip(),content.strip(),memory_type,confidence,metadata_json)
            )

            # fetchone() gives the dict of newly created record
            new_memory=cur.fetchone()

            # record the initial snapshot into memory_history
            insert_history_sql="""
            INSERT INTO memory_history (context_id,operation,subject,content,memory_type,status,metadata) VALUES(%s,%s,%s,%s,%s,%s,%s);
            """

            cur.execute(
                insert_history_sql,
                (
                    new_memory["context_id"],
                    "created",
                    new_memory["subject"],
                    new_memory["content"],
                    new_memory["memory_type"],
                    new_memory["status"],
                    metadata_json
                )
            )

        return new_memory

def get_memory(context_id:int)-> dict:
    if not isinstance(context_id,int) or context_id<=0:
        raise ValueError("context_id must be Non-negative")
    with get_connection() as conn:
        with conn.cursor() as cur:
            select_sql= """
            SELECT context_id, subject, content, memory_type,status, confidence,metadata,valid_after,expires_at,created_at,updated_at FROM context_memory WHERE context_id=%s;
            """
            cur.execute(select_sql,(context_id,))
            record = cur.fetchone()
            return record

def list_memories(include_inactive:bool =False)->list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            if include_inactive:
                select_sql="""
                SELECT context_id, subject, content, memory_type, status,confidence ,metadata,valid_after,expires_at,created_at,updated_at FROM context_memory ORDER BY created_at DESC;
                """
                cur.execute(select_sql)
            else:
                select_sql="""
                SELECT context_id, subject, content, memory_type, status, confidence, 
                           metadata, valid_after, expires_at, created_at, updated_at FROM context_memory WHERE status='active' ORDER BY created_at DESC;
                """
                cur.execute(select_sql)
            records =cur.fetchall()
            return records

def update_memory(
    context_id: int,
    subject:str=None,
    content:str=None,
    memory_type:str= None,
    status:str=None,
    confidence:float=None,
    metadata:dict=None
)-> dict:
    if not isinstance(context_id,int) or context_id <=0:
        raise ValueError("context_id must be positive")

    if status is not None:
        valid_statuses = {'active', 'superseded', 'expired', 'deleted'}
        if status not in valid_statuses:
            raise ValueError(f"invalid status: {status}. Must be one of {valid_statuses}")

    if memory_type is not None:
        valid_types = {'fact', 'preference', 'instruction', 'constraint', 'goal', 'other'}
        if memory_type not in valid_types:
            raise ValueError(f"memory_type invalid: {memory_type}. Permitted are {valid_types}")

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Fetch current record
            cur.execute("SELECT * FROM context_memory WHERE context_id =%s FOR UPDATE;", (context_id,))
            current=cur.fetchone()
            if not current:
                raise ValueError(f"memory of context_id: {context_id} not exists")
            
            # build dynamic update fields
            updates=[]
            params=[]

            if subject is not None:
                updates.append("subject = %s")
                params.append(subject.strip())
            if content is not None:
                updates.append("content= %s")
                params.append(content.strip())
            if memory_type is not None:
                updates.append("memory_type=%s")
                params.append(memory_type)
            if status is not None:
                updates.append("status=%s")
                params.append(status)
            if confidence is not None:
                updates.append("confidence = %s")
                params.append(confidence)
            if metadata is not None:
                updates.append("metadata=%s")
                params.append(json.dumps(metadata))

            if not updates:
                return current # no field changed
            updates.append("updated_at=CURRENT_TIMESTAMP")
            params.append(context_id)

            set_clause = ", ".join(updates)
            update_sql = f"""
                UPDATE context_memory SET {set_clause} WHERE context_id=%s RETURNING context_id, subject, content, memory_type, status, confidence, metadata, created_at, updated_at;
            """
            cur.execute(update_sql,tuple(params))
            updated_memory =cur.fetchone()

            # log updated state in memory_history
            insert_history_sql = """
            INSERT INTO memory_history (context_id,operation,subject,content,memory_type,status,metadata) VALUES (%s,%s,%s,%s,%s,%s,%s);
            """
            metadata_val = updated_memory["metadata"]
            if isinstance(metadata_val, (dict, list)):
                metadata_val = json.dumps(metadata_val)

            cur.execute(
                insert_history_sql,
                (
                    updated_memory["context_id"],
                    "updated",
                    updated_memory["subject"],
                    updated_memory["content"],
                    updated_memory["memory_type"],
                    updated_memory["status"],
                    metadata_val
                )
            )
    return updated_memory

    def soft_delete_memory(context_id: int) -> dict:
   
     if not isinstance(context_id, int) or context_id <= 0:
        raise ValueError("context_id must be a positive integer.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM context_memory WHERE context_id = %s FOR UPDATE;", (context_id,))
            current = cur.fetchone()
            if not current:
                raise ValueError(f"Memory with context_id {context_id} does not exist.")
            if current["status"] == "deleted":
                raise ValueError(f"Memory with context_id {context_id} is already deleted.")

            update_sql = """
                UPDATE context_memory
                SET status = 'deleted', updated_at = CURRENT_TIMESTAMP
                WHERE context_id = %s
                RETURNING context_id, subject, content, memory_type, status, confidence, metadata, created_at, updated_at;
            """
            cur.execute(update_sql, (context_id,))
            deleted_memory = cur.fetchone()

            insert_history_sql = """
                INSERT INTO memory_history (context_id, operation, subject, content, memory_type, status, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cur.execute(
                insert_history_sql,
                (
                    deleted_memory["context_id"],
                    "soft_deleted",
                    deleted_memory["subject"],
                    deleted_memory["content"],
                    deleted_memory["memory_type"],
                    deleted_memory["status"],
                    json.dumps(deleted_memory["metadata"])
                )
            )

            return deleted_memory


def restore_memory(context_id: int) -> dict:
    
    if not isinstance(context_id, int) or context_id <= 0:
        raise ValueError("context_id must be a positive integer.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM context_memory WHERE context_id = %s FOR UPDATE;", (context_id,))
            current = cur.fetchone()
            if not current:
                raise ValueError(f"Memory with context_id {context_id} does not exist.")
            if current["status"] != "deleted":
                raise ValueError(f"Memory with context_id {context_id} is not deleted (current status: {current['status']}).")

            update_sql = """
                UPDATE context_memory
                SET status = 'active', updated_at = CURRENT_TIMESTAMP
                WHERE context_id = %s
                RETURNING context_id, subject, content, memory_type, status, confidence, metadata, created_at, updated_at;
            """
            cur.execute(update_sql, (context_id,))
            restored_memory = cur.fetchone()

            insert_history_sql = """
                INSERT INTO memory_history (context_id, operation, subject, content, memory_type, status, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cur.execute(
                insert_history_sql,
                (
                    restored_memory["context_id"],
                    "restored",
                    restored_memory["subject"],
                    restored_memory["content"],
                    restored_memory["memory_type"],
                    restored_memory["status"],
                    json.dumps(restored_memory["metadata"])
                )
            )

        return restored_memory