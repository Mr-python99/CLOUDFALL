#!/bin/bash
echo "✅ main.py sudah terbaru!"
echo "✅ main.py updated!"
git add main.py
git commit -m "Update main.py"
git pull --rebase origin main
git push origin main
echo "✅ Uploaded to GitHub!"
