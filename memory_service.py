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
    metadata_json = json.dump(metadata)