from select import select
from ast import NotIn
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

