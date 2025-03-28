#!/bin/bash
set -e

# Check if API key is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <api_key>"
    echo "Please provide an API key as an argument"
    exit 1
fi

API_KEY="$1"
echo "Building Docker image..."
docker build -t shabbosgoy-test .

echo "Running test container..."
docker run -it --rm shabbosgoy-test bash -c "
echo \"Running as \$(whoami)\"
echo \"Cloning repository...\"
git clone https://github.com/samrahimi/shabbosgoy.git
cd shabbosgoy

echo \"Building from source...\"
python3 -m pip install --upgrade pip --break-system-packages
python3 -m pip install build wheel --break-system-packages
python3 -m build

echo \"Installing the package...\"
# Find the built wheel file and install it
WHEEL_FILE=\$(find dist -name \"*.whl\" | sort -V | tail -n 1)
if [ -n \"\$WHEEL_FILE\" ]; then
    echo \"Installing wheel: \$WHEEL_FILE\"
    python3 -m pip install \"\$WHEEL_FILE\" --break-system-packages
else
    echo \"No wheel file found, trying to install from source\"
    python3 -m pip install . --break-system-packages
fi

echo \"Testing the installation...\"
# Check if shabbosgoy is in PATH
which shabbosgoy || echo \"Command not found in PATH\"

# Configure the API key
echo \"Configuring shabbosgoy with API key...\"
shabbosgoy --set-config api_key $API_KEY

# Run a meaningful test with a simple prompt
echo \"Running a test prompt...\"
shabbosgoy \"List the current directory files\" || echo \"Failed to run test prompt\"

echo \"Installation test completed.\"
"

echo "Test script created and executed. Check the output above for results."
