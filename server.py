from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'ids_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            token TEXT,
            status TEXT DEFAULT 'idle'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/add_id', methods=['POST'])
def add_id():
    data = request.json
    user_id = data.get('user_id')
    token = data.get('token')
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO accounts (user_id, token, status) VALUES (?, ?, 'idle')", (user_id, token))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"ID {user_id} saved successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_free_id', methods=['GET'])
def get_free_id():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, token FROM accounts WHERE status = 'idle' LIMIT 1")
    row = cursor.fetchone()
    if row:
        user_id, token = row
        cursor.execute("UPDATE accounts SET status = 'busy' WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "user_id": user_id, "token": token}), 200
    else:
        conn.close()
        return jsonify({"status": "empty", "message": "No idle IDs available!"}), 404

@app.route('/get_bulk_ids', methods=['GET'])
def get_bulk_ids():
    limit = int(request.args.get('limit', 50))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, token FROM accounts WHERE status = 'idle' LIMIT ?", (limit,))
    rows = cursor.fetchall()
    if rows:
        accounts_list = []
        for user_id, token in rows:
            accounts_list.append({"user_id": user_id, "token": token})
            cursor.execute("UPDATE accounts SET status = 'busy' WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "count": len(accounts_list), "accounts": accounts_list}), 200
    else:
        conn.close()
        return jsonify({"status": "empty", "message": "No idle IDs available!"}), 404

@app.route('/reset_ids', methods=['GET'])
def reset_ids():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET status = 'idle'")
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "All IDs reset to idle!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
      
