# utils/notes_db.py
import sqlite3
import os
from datetime import datetime
DB_PATH = os.path.join(os.getcwd(), "notes_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # chats: session_id, role, message, timestamp
    c.execute("""CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    message TEXT,
                    timestamp TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    created_at TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    front TEXT,
                    back TEXT,
                    tags TEXT,
                    created_at TEXT
                )""")
    conn.commit()
    conn.close()

def save_chat(session_id, role, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO chats (session_id, role, message, timestamp) VALUES (?, ?, ?, ?)",
              (session_id, role, message, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_chats(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, message, timestamp FROM chats WHERE session_id=? ORDER BY id", (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def save_note(title, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)",
              (title, content, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_notes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, content, created_at FROM notes ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def save_flashcard(front, back, tags=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO flashcards (front, back, tags, created_at) VALUES (?, ?, ?, ?)",
              (front, back, tags, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_flashcards():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, front, back, tags, created_at FROM flashcards ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_note(note_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()

def update_note(note_id, title, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE notes SET title=?, content=? WHERE id=?", (title, content, note_id))
    conn.commit()
    conn.close()