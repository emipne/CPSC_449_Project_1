post: gunicorn3 --bind 127.0.0.1:$PORT --access-logfile - --error-logfile - --log-level debug post_api:app
vote: gunicorn3 --bind 127.0.0.1:$PORT --access-logfile - --error-logfile - --log-level debug vote_api:app
user: gunicorn3 --bind 127.0.0.1:$PORT --access-logfile - --error-logfile - --log-level debug user_api:app
msg: gunicorn3 --bind 127.0.0.1:$PORT --access-logfile - --error-logfile - --log-level debug msg_api:app