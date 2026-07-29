#!/bin/bash
cp dork_db_backup.py dork_db.py
cp animations_backup.py animations.py
echo "✅ Modules updated!"
git add dork_db.py animations.py
git commit -m "Update modules"
git pull --rebase origin main
git push origin main
echo "✅ Uploaded to GitHub!"
