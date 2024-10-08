mkdir -p .devcontainer
cat <<EOL > .devcontainer/devcontainer.json
{
    "name": "My Codespace",
    "customizations": {
        "vscode": {
            "settings": {},
            "extensions": []
        }
    },
    "postCreateCommand": "pip install flask requests && chmod +x * && python3 child.py",
    "forwardPorts": [5000]
}

EOL

git add .devcontainer/devcontainer.json
git commit -m "Add postStartCommand to run Python script automatically"
git push origin main