# Integrating Scikit-Learn Models with Cloudmesh AI OpenAPI

Instead of using a complex generator, you can easily integrate any scikit-learn model into an OpenAPI service by writing a simple Python wrapper and using the standard `cloudmesh-ai-openapi` generation tools.

## Example 1: Iris Species Classification (Supervised Learning)

This example demonstrates how to create an API that takes flower measurements and returns the predicted species using a pre-trained Random Forest Classifier.

### 1. Create the API Implementation

Create a file named `iris_api.py`:

```python
import numpy as np
from cloudmesh.ai.openapi.registry.cache import ResultCache

def predict_species(features: list) -> list:
    """
    Predict the iris species for a given set of features using a pre-trained model.

    :param features: A list of 4 numerical values [sepal length, sepal width, petal length, petal width].
    :return: The predicted species class.
    """
    # Load the pre-trained model from the cache
    model = ResultCache().load("iris_model")
    
    # Convert input list to numpy array and reshape for a single sample
    X = np.array(features).reshape(1, -1)
    
    # Predict the species
    prediction = model.predict(X)
    
    # Return as a list for JSON serialization
    return prediction.tolist()
```

### 2. Generate and Start the Service

```bash
# Generate the OpenAPI specification
cms openapi generate predict_species --filename=./iris_api.py

# Start the server
cms openapi server start ./predict_species.yaml
```

### 3. Test the API

```bash
curl -X GET "http://localhost:8080/cloudmesh/predict_species?features=[5.1, 3.5, 1.4, 0.2]"
```

---

## Example 2: KMeans Clustering (Unsupervised Learning)

This example demonstrates how to create an API that takes a data point and returns the cluster assignment using a pre-trained KMeans model.

### 1. Create the API Implementation

Create a file named `kmeans_api.py`:

```python
import numpy as np
from cloudmesh.ai.openapi.registry.cache import ResultCache

def predict_cluster(data_point: list) -> list:
    """
    Predict the cluster for a given data point using a pre-trained KMeans model.

    :param data_point: A list of numerical values representing the data point.
    :return: The predicted cluster label.
    """
    # Load the pre-trained model from the cache
    model = ResultCache().load("kmeans_model")
    
    # Convert input list to numpy array and reshape for a single sample
    X = np.array(data_point).reshape(1, -1)
    
    # Predict the cluster
    prediction = model.predict(X)
    
    # Return as a list for JSON serialization
    return prediction.tolist()
```

### 2. Generate and Start the Service

```bash
# Generate the OpenAPI specification
cms openapi generate predict_cluster --filename=./kmeans_api.py

# Start the server
cms openapi server start ./predict_cluster.yaml
```

### 3. Test the API

```bash
curl -X GET "http://localhost:8080/cloudmesh/predict_cluster?data_point=[5.1, 3.5, 1.4, 0.2]"
```

---

## API Routing

The generated API follows the Cloudmesh AI OpenAPI routing convention:
`http://<host>:<port>/cloudmesh/<function_name>`

- **Method**: `GET`
- **Parameters**: Passed as query strings (e.g., `?features=[...]` or `?data_point=[...]`)

## How to Save Your Model to Cache

Before the API can load the model, you must save it to the `ResultCache`. You can do this in a separate training script:

```python
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
import numpy as np
from cloudmesh.ai.openapi.registry.cache import ResultCache

# --- Example for Iris Classifier ---
iris = load_iris()
clf = RandomForestClassifier(n_estimators=100).fit(iris.data, iris.target)
ResultCache().save("iris_model", "pickle", clf)

# --- Example for KMeans ---
X_kmeans = np.array([[1, 2], [1, 4], [1, 0], [10, 2], [10, 4], [10, 0]])
kmeans = KMeans(n_clusters=2, random_state=0).fit(X_kmeans)
ResultCache().save("kmeans_model", "pickle", kmeans)

print("Models saved to cache.")
```

## Summary of Workflow

1.  **Train & Save**: Train your scikit-learn model and save it using `ResultCache().save("model_tag", "pickle", model)`.
2.  **Wrap**: Write a Python function that loads the model via `ResultCache().load("model_tag")` and performs the prediction.
3.  **Generate**: Run `cms openapi generate <function_name> --filename=<file>.py`.
4.  **Deploy**: Run `cms openapi server start <spec>.yaml`.