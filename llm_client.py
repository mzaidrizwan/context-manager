from abc import ABC, abstractmethod
import json
import urllib.request
import urllib.error

class BaseLLMClient(ABC):
    @abstractmethod
    def generate(self,prompt:str,system_prompt:str="")->str:
        pass
class LocalLLMClient(BaseLLMClient):
    def __init__(self,host:str = "http://localhost:11434",model_name:str="qwen2.5:0.5b"):
        self.host = host.rstrip("/")
        self.model_name= model_name
    def generate(self,prompt:str,system_prompt:str="")->str:
        url = f"{self.host}/api/generate"
        payload={
            "model":self.model_name,
            "prompt":prompt,
            "system":system_prompt,
            "stream":False
        }

        req = urllib.request.Request(
            url,
            date=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type":"application/json"}
        )

        try:
            with urllib.request.urlopen(req,timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response","").strip()
        except urllib.error.URLError as e:
            raise ConnectionError(f"Local LLM unreachable at {self.host}. Error {e.reason}")

class CloudAPIClient(BaseLLMClient):
    def __init__(self,api_key:str=None):
        self.api_key=api_key
    def generate(self,prompt:str,system_prompt:str="")->str:
        raise NotImplementedError("CloudAPIClient is a placeholder for future cloud integration")