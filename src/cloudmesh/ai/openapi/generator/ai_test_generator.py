import yaml
import requests
from pathlib import Path
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE

class AITestGenerator:
    """
    This class uses an LLM to generate pytest cases from Python code and an OpenAPI spec.
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

    def generate_tests(self, code, openapi_yaml, function_name=None):
        """
        Generates a pytest suite for the given code and OpenAPI specification.
        """
        endpoint = self.llm_config.get("endpoint")
        model = self.llm_config.get("model")
        api_key = self.llm_config.get("api_key")
        
        if not endpoint:
            Console.error("LLM endpoint not configured in config.yaml")
            return None

        prompt = (
            "You are an expert QA engineer. Generate a comprehensive pytest suite for a Python function "
            "that is exposed as an OpenAPI service. \n\n"
            "Requirements:\n"
            "1. Use the 'requests' library to call the API.\n"
            "2. Create a pytest fixture for the base URL.\n"
            "3. Generate tests for all endpoints defined in the OpenAPI spec.\n"
            "4. Include tests for valid inputs and invalid inputs (error handling).\n"
            "5. Ensure the tests are runnable and follow pytest best practices.\n"
            "6. Return ONLY the Python code for the test file.\n\n"
        )
        
        if function_name:
            prompt += f"The target function is: {function_name}\n"
        
        full_prompt = (
            f"{prompt}\n\n"
            f"### Python Implementation:\n```python\n{code}\n```\n\n"
            f"### OpenAPI Specification:\n```yaml\n{openapi_yaml}\n```"
        )
        
        VERBOSE(full_prompt, label="LLM Test Prompt")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert Python QA engineer. Return ONLY the Python code for the pytest file."},
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
            test_code = result["choices"][0]["message"]["content"]
            
            # Clean up markdown code blocks if present
            if "```python" in test_code:
                test_code = test_code.split("```python")[1].split("```")[0]
            elif "```" in test_code:
                test_code = test_code.split("```")[1].split("```")[0]
                
            return test_code.strip()
        except Exception as e:
            Console.error(f"Error calling LLM for test generation: {e}")
            return None