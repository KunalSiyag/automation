#!/bin/bash
# Fix git permissions - run with sudo if needed
cd "$(dirname "$0")"
echo "Fixing git object permissions..."
find .git/objects -type d -user root -exec sudo chown kunalsiyag:kunalsiyag {} \; 2>/dev/null
find .git/objects -type f -user root -exec sudo chown kunalsiyag:kunalsiyag {} \; 2>/dev/null
chmod -R u+w .git/objects
echo "Done! Try committing now."
