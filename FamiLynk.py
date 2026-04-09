from datetime import datetime, timedelta
import requests
import json
import os
import threading
import time

# ===== SETTINGS =====
TOKEN = "8712367782:AAGm-0SGpYlRWZbPhLaKLGbbw-LHWwHS4I0"  # replace with your Telegram bot token
DATA_FILE = "data.json"

# ===== GLOBALS =====
CHAT_ID = ""
data = {}

# ===== TELEGRAM =====
def send_telegram(message):
    if not CHAT_ID:
        print("⚠️ No chat ID set. Telegram message not sent.")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)
        print("✅ Telegram message sent!")
    except Exception as e:
        print(f"❌ Could not send message: {e}")

# ===== DATA HANDLING =====
def load_data():
    global data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except:
            print("⚠️ Data file corrupted. Resetting.")
            data = {"users": {}}
    else:
        data = {"users": {}}

    if "users" not in data:
        data["users"] = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===== USER MANAGEMENT =====
def input_user():
    name = input("Enter user name: ").strip()
    while not name:
        name = input("User name cannot be empty: ").strip()
    if name not in data["users"]:
        data["users"][name] = {"chores": [], "events": [], "bills": [], "groceries": [], "alarms": []}
    print(f"👋 Welcome, {name}!")
    return name

def input_chat_id():
    global CHAT_ID
    CHAT_ID = input("Enter your Telegram chat ID: ").strip()
    while not CHAT_ID.isdigit():
        CHAT_ID = input("Chat ID must be a number! Enter again: ").strip()
    print("✅ Chat ID saved!")

# ===== REMINDERS LOOP =====
def reminders_loop(user_name):
    while True:
        now = datetime.now()
        usr = data["users"][user_name]

        # EVENTS - notify every day before
        for e in usr["events"]:
            try:
                event_dt = datetime.strptime(e["datetime"], "%Y-%m-%d %H:%M")
                if now.date() <= event_dt.date() <= (now.date() + timedelta(days=1)) and not e.get("notified_today"):
                    send_telegram(f"📅 *Upcoming Event!*\n*{e['text']}* at {event_dt.strftime('%I:%M %p, %b %d')}")
                    e["notified_today"] = True
            except:
                continue

        # BILLS - notify 3,1,0 days before
        for b in usr["bills"]:
            try:
                bill_dt = datetime.strptime(b["date"], "%Y-%m-%d")
                days_left = (bill_dt.date() - now.date()).days
                for d in [3,1,0]:
                    key = f"notified_{d}"
                    if days_left == d and not b.get(key):
                        send_telegram(f"💸 *Bill Reminder!*\n*{b['name']}* due in {d} day(s) ({bill_dt.strftime('%b %d')})")
                        b[key] = True
            except:
                continue

        # GROCERIES - notify 2,1,0 days before expiration
        for g in usr["groceries"]:
            try:
                g_dt = datetime.strptime(g["date"], "%Y-%m-%d")
                days_left = (g_dt.date() - now.date()).days
                for d in [2,1,0]:
                    key = f"notified_{d}"
                    if days_left == d and not g.get(key):
                        send_telegram(f"🥦 *Grocery Expiring Soon!*\n*{g['name']}* expires in {d} day(s) ({g_dt.strftime('%b %d')})")
                        g[key] = True
            except:
                continue

        # ALARMS
        for a in usr["alarms"]:
            try:
                alarm_dt = datetime.strptime(a["datetime"], "%Y-%m-%d %H:%M")
                if now >= alarm_dt and not a.get("triggered"):
                    send_telegram(f"⏰ *Alarm!*\n*{a['text']}*")
                    a["triggered"] = True
            except:
                continue

        save_data()
        time.sleep(60)

# ===== HELPER FUNCTIONS =====
def list_items(items, key_text="text", key_date="datetime"):
    if not items:
        print("No items yet.")
        return
    for i, item in enumerate(items,1):
        date_val = item.get(key_date,"")
        text_val = item.get(key_text,"")
        print(f"{i}. {text_val} - {date_val}")

def select_item(items):
    list_items(items)
    if not items:
        return None
    try:
        idx = int(input("Select number: ").strip()) - 1
        if idx < 0 or idx >= len(items):
            print("❌ Invalid number!")
            return None
        return idx
    except:
        print("❌ Invalid input!")
        return None

# ===== EVENTS =====
def events_menu(user_name):
    usr = data["users"][user_name]
    while True:
        print("\n--- EVENTS ---")
        list_items(usr["events"], "text", "datetime")
        print("a. Add  r. Remove  e. Edit  b. Back")
        cmd = input("Choose: ").strip().lower()
        if cmd == "a":
            add_event(user_name)
        elif cmd == "r":
            idx = select_item(usr["events"])
            if idx is not None:
                removed = usr["events"].pop(idx)
                save_data()
                print(f"❌ Removed event: {removed['text']}")
        elif cmd == "e":
            idx = select_item(usr["events"])
            if idx is not None:
                edit_event(user_name, idx)
        elif cmd == "b":
            break
        else:
            print("❌ Invalid option!")

def add_event(user_name):
    usr = data["users"][user_name]
    while True:
        date_str = input("Event date & time (YYYY-MM-DD HH:MM, 24h format): ").strip()
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            if dt < datetime.now():
                print("❌ Date already elapsed! Try again.")
                continue
            break
        except:
            print("❌ Invalid format!")
    text = input("Event description: ").strip()
    usr["events"].append({"datetime": dt.strftime("%Y-%m-%d %H:%M"), "text": text})
    save_data()
    send_telegram(f"📅 *New Event Added!*\n*{text}* at {dt.strftime('%I:%M %p, %b %d')}")

def edit_event(user_name, idx):
    usr = data["users"][user_name]
    event = usr["events"][idx]
    print(f"Editing event: {event['text']} - {event['datetime']}")
    text = input(f"New description (or enter to keep): ").strip()
    date_str = input(f"New date & time YYYY-MM-DD HH:MM (or enter to keep): ").strip()
    if text:
        event["text"] = text
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            if dt < datetime.now():
                print("❌ Date already elapsed! Not updated.")
            else:
                event["datetime"] = dt.strftime("%Y-%m-%d %H:%M")
        except:
            print("❌ Invalid date format. Not updated.")
    save_data()
    print("✅ Event updated!")

# ===== CHORES =====
def chores_menu(user_name):
    usr = data["users"][user_name]
    while True:
        print("\n--- CHORES ---")
        for i,c in enumerate(usr["chores"],1):
            status = "✅ Done" if c.get("done") else "❌ Pending"
            print(f"{i}. {c['name']} - {c['person']} ({status})")
        print("a. Add  d. Done  r. Remove  b. Back")
        cmd = input("Choose: ").strip().lower()
        if cmd == "a":
            add_chore(user_name)
        elif cmd == "d":
            idx = select_item(usr["chores"])
            if idx is not None:
                usr["chores"][idx]["done"] = True
                save_data()
                print("✅ Chore marked as done!")
        elif cmd == "r":
            idx = select_item(usr["chores"])
            if idx is not None:
                removed = usr["chores"].pop(idx)
                save_data()
                print(f"❌ Removed chore: {removed['name']}")
        elif cmd == "b":
            break
        else:
            print("❌ Invalid option!")

def add_chore(user_name):
    usr = data["users"][user_name]
    name = input("Chore name: ").strip()
    person = input("Assigned to: ").strip()
    usr["chores"].append({"name": name, "person": person, "done": False})
    save_data()
    send_telegram(f"🧹 *New Chore Assigned!*\n*{person}*: {name}")

# ===== BILLS =====
def bills_menu(user_name):
    usr = data["users"][user_name]
    while True:
        print("\n--- BILLS ---")
        for i,b in enumerate(usr["bills"],1):
            print(f"{i}. {b['name']} - {b['date']}")
        print("a. Add  r. Remove  e. Edit  b. Back")
        cmd = input("Choose: ").strip().lower()
        if cmd == "a":
            add_bill(user_name)
        elif cmd == "r":
            idx = select_item(usr["bills"])
            if idx is not None:
                removed = usr["bills"].pop(idx)
                save_data()
                print(f"❌ Removed bill: {removed['name']}")
        elif cmd == "e":
            idx = select_item(usr["bills"])
            if idx is not None:
                edit_bill(user_name, idx)
        elif cmd == "b":
            break
        else:
            print("❌ Invalid option!")

def add_bill(user_name):
    usr = data["users"][user_name]
    while True:
        date_str = input("Bill due date (YYYY-MM-DD): ").strip()
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            break
        except:
            print("❌ Invalid format!")
    name = input("Bill name: ").strip()
    usr["bills"].append({"date": dt.strftime("%Y-%m-%d"), "name": name})
    save_data()
    send_telegram(f"💸 *New Bill Added!*\n*{name}* due {dt.strftime('%b %d')}")

def edit_bill(user_name, idx):
    usr = data["users"][user_name]
    bill = usr["bills"][idx]
    print(f"Editing bill: {bill['name']} - {bill['date']}")
    name = input(f"New name (or enter to keep): ").strip()
    date_str = input(f"New due date YYYY-MM-DD (or enter to keep): ").strip()
    if name:
        bill["name"] = name
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            bill["date"] = dt.strftime("%Y-%m-%d")
        except:
            print("❌ Invalid format. Date not updated.")
    save_data()
    print("✅ Bill updated!")

# ===== GROCERIES =====
def groceries_menu(user_name):
    usr = data["users"][user_name]
    while True:
        print("\n--- GROCERIES ---")
        for i,g in enumerate(usr["groceries"],1):
            print(f"{i}. {g['name']} - expires {g['date']}")
        print("a. Add  r. Remove  e. Edit  b. Back")
        cmd = input("Choose: ").strip().lower()
        if cmd == "a":
            add_grocery(user_name)
        elif cmd == "r":
            idx = select_item(usr["groceries"])
            if idx is not None:
                removed = usr["groceries"].pop(idx)
                save_data()
                print(f"❌ Removed grocery: {removed['name']}")
        elif cmd == "e":
            idx = select_item(usr["groceries"])
            if idx is not None:
                edit_grocery(user_name, idx)
        elif cmd == "b":
            break
        else:
            print("❌ Invalid option!")

def add_grocery(user_name):
    usr = data["users"][user_name]
    while True:
        date_str = input("Expiration date (YYYY-MM-DD): ").strip()
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if dt.date() < datetime.now().date():
                print("❌ Date already elapsed! Try again.")
                continue
            break
        except:
            print("❌ Invalid format!")
    name = input("Grocery item name: ").strip()
    usr["groceries"].append({"date": dt.strftime("%Y-%m-%d"), "name": name})
    save_data()
    send_telegram(f"🥦 *New Grocery Added!*\n*{name}* expires {dt.strftime('%b %d')}")

def edit_grocery(user_name, idx):
    usr = data["users"][user_name]
    g = usr["groceries"][idx]
    print(f"Editing grocery: {g['name']} - expires {g['date']}")
    name = input("New name (or enter to keep): ").strip()
    date_str = input("New expiration date YYYY-MM-DD (or enter to keep): ").strip()
    if name:
        g["name"] = name
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if dt.date() >= datetime.now().date():
                g["date"] = dt.strftime("%Y-%m-%d")
            else:
                print("❌ Date already elapsed! Not updated.")
        except:
            print("❌ Invalid format. Date not updated.")
    save_data()
    print("✅ Grocery updated!")

# ===== MAIN MENU =====
def main():
    load_data()
    user_name = input_user()
    input_chat_id()

    t = threading.Thread(target=reminders_loop, args=(user_name,), daemon=True)
    t.start()

    while True:
        print("\n--- MENU ---")
        print("1. Events")
        print("2. Chores")
        print("3. Bills")
        print("4. Groceries")
        print("5. Switch User")
        print("6. Exit")
        choice = input("Choose option: ").strip()
        if choice == "1":
            events_menu(user_name)
        elif choice == "2":
            chores_menu(user_name)
        elif choice == "3":
            bills_menu(user_name)
        elif choice == "4":
            groceries_menu(user_name)
        elif choice == "5":
            user_name = input_user()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option!")

if __name__ == "__main__":
    main()
