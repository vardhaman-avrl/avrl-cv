from fastapi import FastAPI, Request, Form, Query, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import os
from fastapi.responses import RedirectResponse, JSONResponse

# FastAPI App
app = FastAPI()

# Jinja2 Template Directory
templates = Jinja2Templates(directory="templates")

# Database Files
ACCOUNTS_DB = "accounts.db"
PLAYWRIGHT_DB = "playwright_data.db"

# Initialize Databases
def init_databases():
    """Ensure required databases and tables exist."""
    conn = sqlite3.connect(ACCOUNTS_DB)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_name TEXT PRIMARY KEY,
        login_url TEXT,
        username TEXT,
        password TEXT,
        username_selector TEXT,
        password_selector TEXT,
        submit_selector TEXT,
        success_selector TEXT
    )
    """)
    conn.commit()
    conn.close()
    
    conn = sqlite3.connect(PLAYWRIGHT_DB)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_name TEXT,
        timestamp TEXT,
        status TEXT,
        message TEXT
    )
    """)
    conn.commit()
    conn.close()
    print("✅ Databases initialized.")

# Run Database Initialization
init_databases()

# Function to Fetch Only the Latest Login Result Per Account
def get_latest_login_results():
    """Fetch the latest login result for each account."""
    conn = sqlite3.connect(PLAYWRIGHT_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT account_name, status, timestamp
        FROM login_results
        WHERE timestamp = (
            SELECT MAX(timestamp) FROM login_results AS sub 
            WHERE sub.account_name = login_results.account_name
        )
        ORDER BY timestamp DESC
    """)
    results = cursor.fetchall()
    conn.close()
    return results

# Function to Fetch Full Login Log for an Account
def get_full_log(account_name):
    """Fetch the complete log for a specific account."""
    conn = sqlite3.connect(PLAYWRIGHT_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status, timestamp FROM login_results
        WHERE account_name = ?
        ORDER BY timestamp DESC
    """, (account_name,))
    results = cursor.fetchall()
    conn.close()
    return results

# Function to Fetch Accounts
def get_accounts():
    conn = sqlite3.connect(ACCOUNTS_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()
    conn.close()
    return accounts

# Scheduler Function
def scheduled_task():
    os.system("python login_check.py")  # Runs the Playwright script

# Initialize Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, "interval", days=1)
#scheduler.add_job(scheduled_task, "interval", minutes=1)
scheduler.start()

# Dashboard Route (Latest Entries Only)
@app.get("/")
def dashboard(request: Request, filter_status: str = Query(None), filter_account: str = Query(None)):
    results = get_latest_login_results()
    if filter_status:
        results = [row for row in results if row[1] == filter_status]
    if filter_account:
        results = [row for row in results if row[0] == filter_account]
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "results": results, 
        "selected_status": filter_status,
        "selected_account": filter_account
    })

@app.get("/full_log/{account_name}")
def full_log(account_name: str):
    """Fetch the full login history for an account."""
    logs = get_full_log(account_name)
    log_data = [{"status": log[0], "timestamp": log[1]} for log in logs]
    return JSONResponse(content=log_data)

# Manage Accounts Route
@app.get("/accounts")
def manage_accounts(request: Request):
    accounts = get_accounts()
    return templates.TemplateResponse("accounts.html", {"request": request, "accounts": accounts})

# Add Account Route
@app.post("/add_account")
def add_account(
    account_name: str = Form(...), login_url: str = Form(...), username: str = Form(...),
    password: str = Form(...), username_selector: str = Form(...), password_selector: str = Form(...),
    submit_selector: str = Form(...), success_selector: str = Form(...)):
    conn = sqlite3.connect(ACCOUNTS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO accounts (account_name, login_url, username, password, username_selector, 
        password_selector, submit_selector, success_selector)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (account_name, login_url, username, password, username_selector, password_selector, submit_selector, success_selector))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/accounts", status_code=303)

# Edit Account Route
@app.post("/edit_account")
def edit_account(
    account_name: str = Form(...), login_url: str = Form(...), username: str = Form(...),
    password: str = Form(...), username_selector: str = Form(...), password_selector: str = Form(...),
    submit_selector: str = Form(...), success_selector: str = Form(...)):
    conn = sqlite3.connect(ACCOUNTS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE accounts SET login_url=?, username=?, password=?, username_selector=?, 
        password_selector=?, submit_selector=?, success_selector=? WHERE account_name=?
    """, (login_url, username, password, username_selector, password_selector, submit_selector, success_selector, account_name))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/accounts", status_code=303)

# Delete Account Route
@app.post("/delete_account")
def delete_account(account_name: str = Form(...)):
    conn = sqlite3.connect(ACCOUNTS_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE account_name = ?", (account_name,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/accounts", status_code=303)

# Fetch Selectors API
@app.get("/get_selectors")
def get_selectors(website: str = Query(...)):
    conn = sqlite3.connect(ACCOUNTS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT login_url, username_selector, password_selector, submit_selector, success_selector 
        FROM accounts WHERE login_url LIKE ? LIMIT 1
    """, (f"%{website}%",))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "login_url": result[0],
            "username_selector": result[1],
            "password_selector": result[2],
            "submit_selector": result[3],
            "success_selector": result[4]
        }
    return {}

@app.get("/get_account_details")
def get_account_details(account_name: str):
    conn = sqlite3.connect(ACCOUNTS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT account_name, login_url, username, password, username_selector, 
               password_selector, submit_selector, success_selector
        FROM accounts WHERE account_name = ?
    """, (account_name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "account_name": result[0],
            "login_url": result[1],
            "username": result[2],
            "password": result[3],
            "username_selector": result[4],
            "password_selector": result[5],
            "submit_selector": result[6],
            "success_selector": result[7]
        }
    return {}


# Shutdown Hook
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
