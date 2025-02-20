import sqlite3
import datetime
from playwright.sync_api import sync_playwright

# Databases
ACCOUNTS_DB = "accounts.db"
RESULTS_DB = "playwright_data.db"


def init_results_db():
    """Create the login_results table if it doesn't exist."""
    conn = sqlite3.connect(RESULTS_DB)
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

def fetch_all_accounts():
    """Retrieve all account details from the database."""
    conn = sqlite3.connect(ACCOUNTS_DB)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM accounts")
    results = cursor.fetchall()  # Fetch all rows
    
    conn.close()
    
    return results

def save_result(account_name, status, message):
    """Save login attempt result in the database."""
    conn = sqlite3.connect(RESULTS_DB)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO login_results (account_name, timestamp, status, message) VALUES (?, ?, ?, ?)",
                   (account_name, datetime.datetime.now(), status, message))
    
    conn.commit()
    conn.close()

def login_test(account):
    """Run Playwright script for a specific account."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Start in headful mode
        page = browser.new_page()

        print(f"🌍 Navigating to {account['login_url']}")
        page.goto(account["login_url"])

        # Fill in login details dynamically
        page.fill(account["username_selector"], account["username"])
        page.fill(account["password_selector"], account["password"])
        page.click(account["submit_selector"])

        # Wait for success selector (max 15 sec, resolves early if found)
        try:
            page.wait_for_selector(account["success_selector"], timeout=15000)
            print(f"✅ Login successful for {account['account_name']}!")
            save_result(account['account_name'], "success", "User logged in successfully.")
        except:
            print(f"❌ Login failed for {account['account_name']}.")
            save_result(account['account_name'], "failure", "Invalid credentials or error.")
        
        browser.close()

def login_test_all():
    """Run Playwright login test for all accounts in the database."""
    accounts = fetch_all_accounts()
    
    if not accounts:
        print("⚠️ No accounts found in the database.")
        return

    for account in accounts:
        account_data = {
            "account_name": account[0],
            "login_url": account[1],
            "username": account[2],
            "password": account[3],
            "username_selector": account[4],
            "password_selector": account[5],
            "submit_selector": account[6],
            "success_selector": account[7].replace("\"", "\\\""),  # Escape invalid double quotes in selectors
        }
        
        print(f"\n🔄 Running login test for {account_data['account_name']}...")
        login_test(account_data)

# Run login test for all accounts
if __name__ == "__main__":
    init_results_db()  # Ensure table exists before inserting data
    login_test_all()
