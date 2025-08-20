import streamlit as st
import sqlite3, os, random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB_PATH = "db/students.db"
DATA_PATH = "data/ncert_class5_ch1.txt"

def init_db():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS progress (username TEXT, chapter TEXT, flash_correct INT, flash_total INT, quiz_score INT)")
    conn.commit()
    conn.close()

init_db()

def register_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users VALUES (?,?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    data = cur.fetchone()
    conn.close()
    return data is not None

def get_chapter_text():
    with open(DATA_PATH, "r") as f:
        return f.read().splitlines()

def show_dashboard(username):
    st.title(f"📊 Dashboard - {username}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT chapter, flash_correct, flash_total, quiz_score FROM progress WHERE username=?", (username,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        st.info("No progress yet. Start studying!")
        return
    for r in rows:
        ch, fc, ft, qs = r
        acc = f"{int((fc/max(ft,1))*100)}%"
        st.write(f"**{ch}** → Flashcards: {fc}/{ft} ({acc}), Quiz: {qs if qs is not None else 'N/A'}")

def study_mode(username):
    st.title("📖 Study Mode - Chapter 1")
    text = get_chapter_text()
    for line in text[:5]:
        st.write(line)
    q = "What is " + random.choice(["photosynthesis", "fraction", "noun"]) + "?"
    ans = st.text_input(f"Flashcard: {q}")
    if st.button("Submit Answer"):
        correct = bool(ans.strip())
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM progress WHERE username=? AND chapter=?", (username, "Ch1",))
        if cur.fetchone():
            cur.execute("UPDATE progress SET flash_correct=flash_correct+?, flash_total=flash_total+1 WHERE username=? AND chapter=?", (1 if correct else 0, username, "Ch1"))
        else:
            cur.execute("INSERT INTO progress VALUES (?,?,?,?,?)", (username, "Ch1", 1 if correct else 0, 1, None))
        conn.commit()
        conn.close()
        st.success("Answer saved!")

def quiz_mode(username):
    st.title("📝 Quiz Mode - Chapter 1")
    q1 = st.radio("Q1: 2+3=?", ["4","5","6"])
    if st.button("Submit Quiz"):
        score = 1 if q1=="5" else 0
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE progress SET quiz_score=? WHERE username=? AND chapter=?", (score, username, "Ch1"))
        conn.commit()
        conn.close()
        st.success(f"Quiz submitted. Score: {score}/1")

def doubt_mode(username):
    st.title("💡 Doubt Clearing")
    query = st.text_input("Ask your question:")
    if st.button("Get Answer"):
        docs = get_chapter_text()
        vectorizer = TfidfVectorizer().fit(docs+[query])
        vectors = vectorizer.transform(docs+[query])
        sims = cosine_similarity(vectors[-1], vectors[:-1])
        best_idx = sims.argmax()
        st.write("Answer:", docs[best_idx])
