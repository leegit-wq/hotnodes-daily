#!/usr/bin/env bash
set -e
echo "Starting deploy script..."
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || true
# Register cron job: daily 02:00 run agent
(crontab -l 2>/dev/null; echo "0 2 * * * cd $(pwd) && /usr/bin/python3 $(pwd)/agent.py >> $(pwd)/agent.log 2>&1") | crontab -
echo "Deploy finished."
