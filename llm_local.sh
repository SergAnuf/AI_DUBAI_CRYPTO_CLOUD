#!/bin/bash

# Update the system
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install essential dependencies (if not already installed)
echo "Installing dependencies..."
sudo apt install -y curl python3-pip

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Installing Ollama..."
    pip install ollama
else
    echo "Ollama is already installed."
fi

# Set the model size (change the value as needed)
model_size="7"  # Predefined model size (3, 7, 13, or 30)

# Install the selected model
case "$model_size" in
    3)
        echo "Installing 3B model..."
        ollama pull 3B-model
        ;;
    7)
        echo "Installing 7B model..."
        ollama pull 7B-model
        ;;
    13)
        echo "Installing 13B model..."
        ollama pull 13B-model
        ;;
    30)
        echo "Installing 30B model..."
        ollama pull 30B-model
        ;;
    *)
        echo "Invalid model size selected. Please choose from 3, 7, 13, or 30."
        exit 1
        ;;
esac

echo "Model installation complete."
