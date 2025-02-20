# AVRL-CV

**AVRL-CV** is a Playwright-based web automation project that automates login testing, schedules tasks, and provides a FastAPI-powered dashboard for managing accounts and viewing results.

## 🚀 Features
- ✅ **Automated Login Testing** using Playwright.
- ✅ **FastAPI Dashboard** to view login results.
- ✅ **Manage Accounts** (Add, Edit, Delete).
- ✅ **Custom Scheduler** to run login tests periodically.
- ✅ **Bootstrap UI** for better user experience.
- ✅ **History Tracking** with full logs.

## 📂 Project Structure
```
avrl-cv/
│── main.py                # FastAPI app (dashboard, API, scheduler)
│── login_check.py      # Playwright login automation script
│── templates/
│   ├── dashboard.html     # Dashboard UI
│   ├── accounts.html      # Manage accounts UI
│── README.md              # Documentation
```

## 🛠️ Setup & Installation
### 1️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 2️⃣ Run the Server
```sh
uvicorn main:app --reload
```
FastAPI will start at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 3️⃣ Access Dashboard
- **Dashboard:** [`/`](http://127.0.0.1:8000) (View login results)
- **Manage Accounts:** [`/accounts`](http://127.0.0.1:8000/accounts) (Add/Edit/Delete accounts)

### 4️⃣ Run Playwright Automation
```sh
python login_test_all.py
```

## ⏳ Scheduler
- Runs login tests **once every 24 hours** by default.
- Modify `main.py` to change scheduling frequency.

## 🛠️ Updates
- Authorization
