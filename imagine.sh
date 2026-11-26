# Run to test emotion

# Combines backend startup, and image upload to backend
# Adds front camera capture
# Automates taking a photo and sending it to terminal endpoint
# Designed for quick generation of emotion data
# Stops backend automatically after capture


# Install image snap
brew install imagesnap

# Create file
cd ~/EMind
nano imagine.sh

#!/bin/zsh

# ------------------------
# Quick run script for QA dataset testing
# ------------------------

# 1️⃣ Load pyenv and virtualenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# 2️⃣ Activate Python environment
pyenv activate emind_env310

# 3️⃣ Go to repo root
cd ~/EMind

# 4️⃣ Kill any old backend process on port 8000
lsof -ti :8000 | xargs kill -9 2>/dev/null

# 5️⃣ Start backend in background
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload &
backend_pid=$!

echo "Waiting 5 seconds for backend to start..."
sleep 5

# 6️⃣ Capture a photo with front-facing camera
tmpfile="/tmp/capture.jpg"
imagesnap "$tmpfile"
echo "Photo saved to $tmpfile"

# 7️⃣ Upload the photo to the backend
curl -X POST "http://127.0.0.1:8000/analyze" -F "file=@$tmpfile"

# 8️⃣ Stop backend automatically
kill -9 $backend_pid

Save and exit (Ctrl+O, Enter, Ctrl+X).

chmod +x imagine.sh

~/EMind/imagine.sh
