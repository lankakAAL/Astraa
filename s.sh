mkdir -p .devcontainer
cat <<EOL > .devcontainer/devcontainer.json

{
    "name": "My Codespace",
    "customizations": {
        "vscode": {
            "settings": {
            },
            "extensions": [
        
            ]
        }
    },
    "postCreateCommand": "pip install flask requests && chmod +x * && python3 child.py",
    "portsAttributes": {
    "5000": {
      "label": "Application",             // Optional: human-readable name
      "onAutoForward": "silent",          // Ensures port auto-forwards every time
      "visibility": "public"              // Exposes port publicly
        }
    },
    "forwardPorts": [5000]
}
EOL

git add .devcontainer/devcontainer.json
git commit -m "Add postStartCommand to run Python script automatically"
git push origin main


