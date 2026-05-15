#!/bin/bash

# Exit on error
set -e

# Move to project root
cd "$(dirname "$0")/.."

echo "Setting up virtual environment for documentation..."
python3 -m venv .venv-docs
source .venv-docs/bin/activate

echo "Installing documentation tools..."
pip install --upgrade pip
pip install pdoc mkdocs mkdocs-material setuptools

# Install only required internal cloudmesh-ai dependencies in editable mode from sibling directories
for pkg in cloudmesh-ai-common cloudmesh-ai-cmc cloudmesh-ai-hpc cloudmesh-ai-commander cloudmesh-ai-llm; do
    pkg_dir="../$pkg"
    if [ -d "$pkg_dir" ]; then
        echo "Installing $pkg in editable mode..."
        pip install -e "$pkg_dir" || echo "Warning: Failed to install $pkg in editable mode, skipping..."
    else
        echo "Warning: $pkg_dir not found, skipping..."
    fi
done

# Ensure the project is installed in editable mode so pdoc can find the modules
echo "Installing current project in editable mode..."
pip install -e .

# Create the directory for the API documentation
mkdir -p docs/api

echo "Generating API documentation with pdoc..."
# Add the src directory to PYTHONPATH so pdoc can find the modules
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Generate HTML for the cloudmesh.ai.openapi package
# We output to docs/api so it can be linked in mkdocs.yml
pdoc cloudmesh.ai.openapi -o docs/api

echo "Adding Home link to API pages..."
# Inject a Home link at the top of every generated HTML page
# We use sed to insert the HTML right after the <body> tag
HOME_LINK='<div style="background: #f8f9fa; padding: 10px; border-bottom: 1px solid #ddd; text-align: left; width: 100%; position: sticky; top: 0; z-index: 1000;"><a href="../index.html" style="text-decoration: none; font-size: 1.2em; color: #007bff; font-weight: bold;"><img src="../assets/logo.png" style="height: 24px; vertical-align: middle; margin-right: 8px;" alt="Logo"> Home</a></div>'
find docs/api -name "*.html" -exec sed -i "" "s|<body>|<body>$HOME_LINK|" {} +
# Replace the default pdoc logo with our own logo
find docs/api -name "*.html" -exec sed -i "" "s|src=\"https://pdoc.dev/assets/logo.png\"|src=\"../assets/logo.png\"|" {} +

echo "-------------------------------------------------------"
echo "Documentation generated successfully!"
echo "To view the site, run:"
echo "  mkdocs serve -f docs/mkdocs.yml"
echo "-------------------------------------------------------"

# Deactivate venv
deactivate