import streamlit as st
import sqlite3
from datetime import datetime

# ---------- UI ----------
st.set_page_config(page_title="Sreevas Autoconsultancy", layout="wide")

st.markdown("""
<style>
.stButton>button {
    border-radius: 12px;
    padding: 10px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------- DATABASE ----------
conn = sqlite3.connect("sreevas.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS work (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_name TEXT,
    vehicle TEXT,
    chassis TEXT,
    owner TEXT,
    phone TEXT,
    ro_phone TEXT,
    task TEXT,
    total REAL,
    advance REAL,
    balance REAL,
    date TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_name TEXT,
    vehicle TEXT,
    chassis TEXT,
    owner TEXT,
    phone TEXT,
    ro_phone TEXT,
    task TEXT,
    total REAL,
    advance REAL,
    balance REAL,
    date TEXT
)
""")

conn.commit()

# ---------- LOGIN ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Sreevas Autoconsultancy Login")
    email = st.text_input("Enter Email")

    if st.button("Login"):
        if email == "sreevasranni@gmail.com":
            st.session_state.logged_in = True
        else:
            st.error("Wrong Email")

# ---------- MAIN ----------
if st.session_state.logged_in:

    st.title("🚗 Sreevas Autoconsultancy Dashboard")

    tabs = st.tabs(["🏠 Home", "➕ Add Work", "📜 History"])

    # ================= HOME =================
    with tabs[0]:
        st.subheader("Employees")

        c.execute("SELECT name FROM employees")
        employees = c.fetchall()

        cols = st.columns(3)

        for i, emp in enumerate(employees):
            emp_name = emp[0]

            work_count = c.execute(
                "SELECT COUNT(*) FROM work WHERE emp_name=?",
                (emp_name,)
            ).fetchone()[0]

            with cols[i % 3]:
                if st.button(f"👤 {emp_name}\n📌 {work_count} Tasks", key=emp_name):
                    st.session_state.selected_emp = emp_name

        st.write("---")

        # ADD EMPLOYEE
        new_emp = st.text_input("Add Employee")
        if st.button("Add Employee"):
            if new_emp.strip():
                try:
                    c.execute("INSERT INTO employees (name) VALUES (?)", (new_emp,))
                    conn.commit()
                    st.success("Employee added")
                except:
                    st.error("Already exists")

        # EMPLOYEE PAGE
        if "selected_emp" in st.session_state:
            emp_name = st.session_state.selected_emp
            st.subheader(f"📋 {emp_name}'s Work")

            c.execute("SELECT * FROM work WHERE emp_name=?", (emp_name,))
            works = c.fetchall()

            for w in works:
                work_id = w[0]

                st.markdown(f"""
                ### 🚗 {w[2]}
                👤 Owner: {w[4]}  
                📞 Phone: {w[5]}  
                🆔 Chassis: {w[3]}  
                💰 Total: {w[8]} | Advance: {w[9]} | Balance: {w[10]}  
                📅 {w[11]}
                """)

                # MULTI TASK SYSTEM
                tasks = w[7].split(",")

                completed_count = 0

                st.write("### Tasks:")
                for i, task in enumerate(tasks):
                    key = f"{work_id}_{i}"
                    if st.checkbox(task.strip(), key=key):
                        completed_count += 1

                # ONLY WHEN ALL TASKS DONE
                if completed_count == len(tasks):
                    if st.button("✅ Finish Work", key=f"finish_{work_id}"):

                        c.execute("""
                            INSERT INTO history (emp_name, vehicle, chassis, owner, phone, ro_phone, task, total, advance, balance, date)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)
                        """, (w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8], w[9], w[10], w[11]))

                        c.execute("DELETE FROM work WHERE id=?", (work_id,))
                        conn.commit()

                        st.success("Work moved to history!")

            if st.button("⬅ Back"):
                del st.session_state.selected_emp

    # ================= ADD WORK =================
    with tabs[1]:
        st.subheader("Assign Work")

        c.execute("SELECT name FROM employees")
        emp_list = [e[0] for e in c.fetchall()]

        if emp_list:
            emp = st.selectbox("Employee", emp_list)

            vehicle = st.text_input("Vehicle Number")
            chassis = st.text_input("Chassis Number")
            owner = st.text_input("Owner Name")
            phone = st.text_input("Phone Number")
            ro_phone = st.text_input("RO Phone")

            # TASK SYSTEM
            if "tasks" not in st.session_state:
                st.session_state.tasks = []

            col1, col2 = st.columns([3,1])
            with col1:
                new_task = st.text_input("Add Task")
            with col2:
                if st.button("➕"):
                    if new_task.strip():
                        st.session_state.tasks.append(new_task.strip())

            st.write("### Tasks Added:")
            for t in st.session_state.tasks:
                st.write(f"• {t}")

            # CASH
            total = st.number_input("Total Cash", min_value=0.0)
            advance = st.number_input("Advance Cash", min_value=0.0)
            balance = total - advance

            st.info(f"💰 Balance Cash: {balance}")

            # DATE
            date_input = st.date_input("Select Date")

            if st.button("Save Work"):
                if st.session_state.tasks:
                    all_tasks = ",".join(st.session_state.tasks)

                    c.execute(
                        "INSERT INTO work (emp_name, vehicle, chassis, owner, phone, ro_phone, task, total, advance, balance, date) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (emp, vehicle, chassis, owner, phone, ro_phone, all_tasks, total, advance, balance, str(date_input))
                    )
                    conn.commit()

                    st.success("Work Added Successfully!")
                    st.session_state.tasks = []
                else:
                    st.warning("Add at least one task")

        else:
            st.warning("Add employees first")

    # ================= HISTORY =================
    with tabs[2]:
        st.subheader("History")

        c.execute("SELECT * FROM history")
        hist = c.fetchall()

        for h in hist:
            st.markdown(f"""
            👤 {h[1]}  
            🚗 {h[2]}  
            🔧 {h[7]}  
            💰 {h[8]}  
            📅 {h[11]}
            ---
            """)

        if st.button("🗑 Clear History"):
            c.execute("DELETE FROM history")
            conn.commit()
            st.success("History Cleared")