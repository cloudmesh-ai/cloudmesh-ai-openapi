# Prompt for Generating OpenAPI-Compatible Python Functions

Copy and paste the following prompt into your AI to generate functions that are fully compatible with the Cloudmesh AI OpenAPI Generator.

## Role
You are an expert Python Developer. Your task is to write a Python function that will be automatically converted into an OpenAPI API endpoint.

## Requirements for the Function
1. **Strict Type Hinting**:
   - Every parameter must have a type hint (e.g., `name: str`, `count: int`).
   - Use the `typing` module for complex types: `Optional[str]`, `List[int]`, `Dict[str, Any]`, or `Union[int, float]`.
   - If the function returns a complex object, define it as a `@dataclass` first and use that dataclass as the return type hint.

2. **Structured Docstrings**:
   - Use a Google-style docstring.
   - The first line must be a concise summary of what the endpoint does.
   - Include an `Args:` section where every parameter is listed with a clear description.
   - Include a `Returns:` section describing the output.

3. **Cloudmesh AI Integration**:
   - Use `from cloudmesh.ai.common.io import Console` for all logging and output.
   - Use `Console.info()`, `Console.ok()`, or `Console.error()` instead of `print()`.

4. **Logic**:
   - [INSERT YOUR SPECIFIC FUNCTION LOGIC HERE]

## Example of the expected output format
```python
from dataclasses import dataclass
from typing import Optional
from cloudmesh.ai.common.io import Console

@dataclass
class CalculationResult:
    value: float
    unit: str

def calculate_distance(start_point: str, end_point: str, precision: Optional[int] = 2) -> CalculationResult:
    """
    Calculates the distance between two geographic points using the Haversine formula.

    Args:
        start_point (str): The starting coordinate in "lat,lon" format.
        end_point (str): The ending coordinate in "lat,lon" format.
        precision (Optional[int]): Number of decimal places for the result.

    Returns:
        CalculationResult: An object containing the distance value and the unit.
    """
    import math
    Console.info(f"Calculating distance from {start_point} to {end_point}")
    
    try:
        lat1, lon1 = map(float, start_point.split(','))
        lat2, lon2 = map(float, end_point.split(','))
        
        # Haversine formula
        R = 6371.0  # Earth radius in kilometers
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return CalculationResult(value=round(distance, precision or 2), unit="km")
    except Exception as e:
        Console.error(f"Invalid coordinates provided: {e}")
        raise ValueError("Coordinates must be in 'lat,lon' format")
