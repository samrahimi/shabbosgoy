#!/bin/bash
set -e

echo "Building Docker image..."
docker build -t shabbosgoy-test .

echo "Running test container..."
docker run -it --rm shabbosgoy-test bash -c '
echo "Running as $(whoami)"
echo "Cloning repository..."
git clone https://github.com/samrahimi/shabbosgoy.git
cd shabbosgoy

echo "Building from source..."
python3 -m pip install --upgrade pip
python3 -m pip install build wheel
python3 -m build

echo "Installing the package..."
# Find the built wheel file and install it
WHEEL_FILE=$(find dist -name "*.whl" | sort -V | tail -n 1)
if [ -n "$WHEEL_FILE" ]; then
    echo "Installing wheel: $WHEEL_FILE"
    python3 -m pip install "$WHEEL_FILE"
else
    echo "No wheel file found, trying to install from source"
    python3 -m pip install .
fi

echo "Testing the installation..."
# Assuming the command is called "shabbosgoy"
which shabbosgoy || echo "Command not found in PATH"
shabbosgoy --version || echo "Failed to get version"
echo "Installation test completed."
'
