import yaml
import requests
from pathlib import Path
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE

class AIGenerator:
    """
    This class uses an LLM to generate OpenAPI specifications from Python code.
    """

    def __init__(self, config_path=None):
        if config_path is None:
            # Default path relative to this file
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        self.config = self._load_config(config_path)
        self.llm_config = self.config.get("llm", {})
        self.gen_config = self.config.get("generation", {})

    def _load_config(self, path):
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            Console.error(f"Failed to load config from {path}: {e}")
            return {}

    def generate(self, code, function_name=None):
        """
        Generates an OpenAPI specification for the given code.
        """
        endpoint = self.llm_config.get("endpoint")
        model = self.llm_config.get("model")
        api_key = self.llm_config.get("api_key")
        
        if not endpoint:
            Console.error("LLM endpoint not configured in config.yaml")
            return None

        prompt = self.gen_config.get("prompt_template", "Generate an OpenAPI 3.0 specification for the following Python code:")
        if function_name:
            prompt += f" Focus on the function: {function_name}"
        
        full_prompt = f"{prompt}\n\n```python\n{code}\n```"
        
        VERBOSE(full_prompt, label="LLM Prompt")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert OpenAPI specification generator. Return ONLY the YAML content."},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": self.llm_config.get("temperature", 0.7)
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{endpoint}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.llm_config.get("timeout", 30)
            )
            response.raise_for_status()
            result = response.json()
            openapi_yaml = result["choices"][0]["message"]["content"]
            
            # Clean up markdown code blocks if present
            if "```yaml" in openapi_yaml:
                openapi_yaml = openapi_yaml.split("```yaml")[1].split("```")[0]
            elif "```" in openapi_yaml:
                openapi_yaml = openapi_yaml.split("```")[1].split("```")[0]
                
            return openapi_yaml.strip()
        except Exception as e:
            Console.error(f"Error calling LLM: {e}")
            return None