import xmlrpc.server
import threading
import sqlite3
import os
from typing import List
from xmlrpc.server import SimpleXMLRPCServer
from datetime import datetime

# 添加 is_deleted 欄位（如不存在）
def add_is_deleted_column():
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    try:
        # 嘗試添加 is_deleted 欄位
        cursor.execute("ALTER TABLE topics ADD COLUMN is_deleted INTEGER DEFAULT 0")
        conn.commit()
        print("is_deleted column added to topics table.")
    except sqlite3.OperationalError:
        print("Column 'is_deleted' already exists.")
    finally:
        conn.close()

# 初始化資料庫並創建表格
def init_db():
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()

    # 創建使用者表格
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')

    # 創建討論主題表格
    cursor.execute('''CREATE TABLE IF NOT EXISTS topics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        author TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_deleted INTEGER DEFAULT 0,
                        FOREIGN KEY (author) REFERENCES users(username)
                    )''')

    # 創建回覆表格
    cursor.execute('''CREATE TABLE IF NOT EXISTS replies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic_id INTEGER,
                        content TEXT NOT NULL,
                        author TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (author) REFERENCES users(username),
                        FOREIGN KEY (topic_id) REFERENCES topics(id)
                    )''')

    # 創建 actions 表格
    cursor.execute('''CREATE TABLE IF NOT EXISTS actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        action_type TEXT NOT NULL,
                        action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (username) REFERENCES users(username)
                    )''')

    conn.commit()
    conn.close()
    add_is_deleted_column()

# 初始化資料庫
init_db()

# 紀錄操作到 actions 表格
def log_action(username: str, action_type: str):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO actions (username, action_type) VALUES (?, ?)", (username, action_type))
    conn.commit()
    conn.close()

class ChatServer:
    def __init__(self):
        self.shutdown_event = threading.Event()
        self.topic_lock = threading.Lock()
        init_db()

    def register(self, username: str, password: str) -> str:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            conn.close()
            return "Error: Username already exists."
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        log_action(username, "register")
        return f"User {username} registered successfully."

    def login(self, username: str, password: str) -> str:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        if result is None:
            conn.close()
            return "Error: Username does not exist."
        stored_password = result[0]
        if stored_password != password:
            conn.close()
            return "Incorrect password"
        conn.close()
        log_action(username, "login")
        return f"User {username} logged in successfully."

    def create(self, username: str, title: str, content: str) -> str:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        if not cursor.fetchone():
            conn.close()
            return "Error: You must register first."
        cursor.execute("INSERT INTO topics (title, content, author, is_deleted) VALUES (?, ?, ?, 0)", (title, content, username))
        topic_id = cursor.lastrowid
        conn.commit()
        conn.close()
        log_action(username, "create_topic")
        return f"Topic '{title}' created with new ID {topic_id}."

    def subject(self) -> List[str]:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author FROM topics WHERE is_deleted=0")
        topics = cursor.fetchall()
        conn.close()
        return [f"ID {topic[0]}: {topic[1]} (by {topic[2]})" for topic in topics]

    def reply(self, username: str, topic_id: int, content: str) -> str:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        if not cursor.fetchone():
            conn.close()
            return "Error: You must register first."
        cursor.execute("SELECT id FROM topics WHERE id=? AND is_deleted=0", (topic_id,))
        if not cursor.fetchone():
            conn.close()
            return "Error: Topic not found or has been deleted."
        cursor.execute("INSERT INTO replies (topic_id, content, author) VALUES (?, ?, ?)", (topic_id, content, username))
        conn.commit()
        conn.close()
        log_action(username, "reply")
        return f"{username} replied to topic ID {topic_id}."

    def get_user_actions(self, username: str) -> List[str]:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT action_type, action_time FROM actions WHERE username=? ORDER BY action_time DESC", (username,))
        actions = cursor.fetchall()
        conn.close()
        return [f"{action[1]} - {action[0]}" for action in actions]

    def discussion(self, topic_id: int) -> str:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title, content, author, created_at FROM topics WHERE id=? AND is_deleted=0", (topic_id,))
        topic = cursor.fetchone()
        if not topic:
            conn.close()
            return "Error: Topic not found or has been deleted."
        result = f"Title: {topic[0]}\nContent: {topic[1]}\nAuthor: {topic[2]}\nPosted at: {topic[3]}\nReplies:\n"
        cursor.execute("SELECT id, content, author, created_at FROM replies WHERE topic_id=?", (topic_id,))
        replies = cursor.fetchall()
        for reply in replies:
            result += f" - ID {reply[0]} by {reply[2]} at {reply[3]}: {reply[1]}\n"
        conn.close()
        return result

    def delete(self, username: str, item_id: int) -> str:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author FROM topics WHERE id=?", (item_id,))
        topic = cursor.fetchone()
        if topic:
            if topic[2] != username:
                conn.close()
                return "Error: Only the author can delete this topic."
            cursor.execute("UPDATE topics SET is_deleted=1 WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            log_action(username, "delete_topic")
            return f"Topic '{topic[1]}' deleted."
        cursor.execute("SELECT id, content, author FROM replies WHERE id=?", (item_id,))
        reply = cursor.fetchone()
        if reply:
            if reply[2] != username:
                conn.close()
                return "Error: Only the author can delete this reply."
            cursor.execute("DELETE FROM replies WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            log_action(username, "delete_reply")
            return f"Reply ID {item_id} deleted."
        conn.close()
        return "Error: Item not found."

    def shutdown(self) -> bool:
        print("Server shutdown... Goodbye.")
        self.shutdown_event.set()
        return True

def run_server(cs: ChatServer):
    server = SimpleXMLRPCServer(("localhost", 3410), allow_none=True)
    server.register_instance(cs)
    print(f"Listening on port 3410...")
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    cs.shutdown_event.wait()
    server.shutdown()
    server_thread.join()

if __name__ == "__main__":
    cs = ChatServer()
    run_server(cs)
