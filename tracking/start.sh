echo Starting autonomous mode
gunicorn --reload --timeout 6000 -w 1 --bind 0.0.0.0:6001 main:app