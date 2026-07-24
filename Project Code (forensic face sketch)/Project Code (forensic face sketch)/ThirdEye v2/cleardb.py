import sqlite3
conn = sqlite3.connect('login.sqlite')
cursor = conn.cursor()
cursor.execute('DELETE FROM login_data')
conn.commit()
conn.close()
print("DB Cleared")
