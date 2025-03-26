import os

os.system('echo y | plink -pw "Yhy13243546" "root@47.108.139.79" "cd /var/www/ds/backend && python3 -c \\\"import sqlite3; conn = sqlite3.connect(\'app.db\'); cursor = conn.cursor(); cursor.execute(\'SELECT id, username, email, role FROM users\'); print(cursor.fetchall()); conn.close()\\\""') 