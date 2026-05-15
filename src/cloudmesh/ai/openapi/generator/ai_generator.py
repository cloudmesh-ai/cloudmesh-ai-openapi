import yaml
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from cloudmesh.ai.common.io import Console
from cloudmesh.ai.common.debug import VERBOSE
try:
    from openapi_spec_validator import validate_spec
except ImportError:
    validate_spec = None

class AIGenerator:
    """Uses an LLM to generate OpenAPI specifications from Python code."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initializes the AIGenerator.

        Args:
            config_path (Optional[Path]): Path to the configuration YAML file. 
                Defaults to config.yaml in the parent directory.
        """
        if config_path is None:
            # Default path relative to this file
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        self.config: Dict[str, Any] = self._load_config(config_path)
        self.llm_config: Dict[str, Any] = self.config.get("llm", {})
        self.gen_config: Dict[str, Any] = self.config.get("generation", {})

    def _load_config(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, IOError) as e:
            Console.error(f"Failed to load config from {path}: {e}")
            return {}

    def _get_few_shot_examples(self) -> str:
        """Load examples from the examples/ directory to use for few-shot prompting.

        Expects pairs of .py and .yaml files with the same base name.

        Returns:
            str: A formatted string containing the few-shot examples.
        """
        examples_dir = Path(__file__).parent.parent / "examples"
        if not examples_dir.exists():
            return ""

        examples_text = "Here are some examples of Python code and their corresponding OpenAPI specifications:\n\n"
        py_files = list(examples_dir.glob("*.py"))
        
        for py_file in py_files:
            yaml_file = py_file.with_suffix(".yaml")
            if yaml_file.exists():
                with open(py_file, "r") as f_py, open(yaml_file, "r") as f_yaml:
                    examples_text += f"Code:\n```python\n{f_py.read()}\n```\n"
                    examples_text += f"OpenAPI Spec:\n```yaml\n{f_yaml.read()}\n```\n\n"
        
        return examples_text if len(py_files) > 0 else ""

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Internal method to handle the LLM API call.

        Args:
            prompt (str): The prompt to send to the LLM.

        Returns:
            Optional[str]: The generated OpenAPI YAML content, or None if the call failed.
        """
        endpoint = self.llm_config.get("endpoint")
        model = self.llm_config.get("model")
        api_key = self.llm_config.get("api_key")
        
        if not endpoint:
            Console.error("LLM endpoint not configured in config.yaml")
            return None

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert OpenAPI specification generator. Return ONLY the YAML content."},
                {"role": "user", "content": prompt}
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
            
            if not result.get("choices"):
                return None
                
            openapi_yaml = result["choices"][0]["message"]["content"]
            
            if "```yaml" in openapi_yaml:
                openapi_yaml = openapi_yaml.split("```yaml")[1].split("```")[0]
            elif "```" in openapi_yaml:
                openapi_yaml = openapi_yaml.split("```")[1].split("```")[0]
                
            return openapi_yaml.strip()
        except Exception as e:
            Console.error(f"LLM call failed: {e}")
            return None

    def generate(self, code: str, function_name: Optional[str] = None) -> Optional[str]:
        """Generates an OpenAPI specification for the given code with a validation loop.

        Args:
            code (str): The Python source code to analyze.
            function_name (Optional[str]): The specific function name to focus on.

        Returns:
            Optional[str]: The validated OpenAPI YAML specification, or None if generation failed.
        """
        prompt_template = self.gen_config.get("prompt_template", "Generate an OpenAPI 3.0 specification for the following Python code:")
        if function_name:
            prompt_template += f" Focus on the function: {function_name}"
        
        few_shot = self._get_few_shot_examples()
        full_prompt = f"{few_shot}\n{prompt_template}\n\n```python\n{code}\n```"
        
        VERBOSE(full_prompt, label="LLM Prompt")

        max_retries = self.gen_config.get("max_retries", 3)
        current_prompt = full_prompt

        for attempt in range(max_retries):
            openapi_yaml = self._call_llm(current_prompt)
            if not openapi_yaml:
                continue

            try:
                # 1. Basic YAML syntax check
                spec_dict = yaml.safe_load(openapi_yaml)
                
                # 2. OpenAPI Specification validation
                if validate_spec:
                    validate_spec(spec_dict)
                
                return openapi_yaml # Valid OpenAPI Spec
            except (yaml.YAMLError, Exception) as e:
                Console.info(f"Attempt {attempt + 1} failed validation: {e}. Retrying...")
                current_prompt = f"The previous OpenAPI spec you generated was invalid:\n{openapi_yaml}\n\nError: {e}\n\nPlease correct the specification and return ONLY the valid YAML content."
        
        Console.error(f"Failed to generate valid OpenAPI spec after {max_retries} attempts.")
        return None
