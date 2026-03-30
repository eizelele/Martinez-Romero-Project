from datetime import datetime
import requests
import json
import os
import threading
import time

# ===== CONFIG =====
TOKEN = "8712367782:AAGm-0SGpYlRWZbPhLaKLGbbw-LHWwHS4I0"  # Telegram bot token
DATA_FILE = "data.json"
REMINDER_INTERVAL = 60  # in seconds

# ===== GLOBALS =====
CHAT_ID = ""
current_family = ""
data = {}

# ===== TELEGRAM FUNCTION =====
def send_telegram(message):
    if not CHAT_ID:
        print("No chat ID set! Telegram message not sent.")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
        print("Message sent via Telegram")
    except Exception as e:
        print(f"Could not send message: {e}")

# ===== LOAD/SAVE DATA =====
def load_data():
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"families": {}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===== FAMILY HANDLING =====
def input_family():
    global current_family
    name = input("Enter family name: ").strip()
    while not name:
        name = input("Enter family name: ").strip()
    current_family = name
    if name not in data["families"]:
        data["families"][name] = {"events": [], "chores": [], "bills": [], "groceries": []}
    save_data()
    print(f"\nWelcome, {name} Family!")

def get_family_data():
    return data["families"][current_family]

# ===== CHAT ID =====
def input_chat_id():
    global CHAT_ID
    CHAT_ID = input("Enter your Telegram chat ID: ").strip()
    while not CHAT_ID.isdigit():
        CHAT_ID = input("Chat ID must be a number! Enter your Telegram chat ID: ").strip()
    print("Chat ID saved!")

# ===== HELPERS =====
def print_menu():
    print("\n--- MENU ---")
    print("1. Events")
    print("2. Chores")
    print("3. Bills")
    print("4. Groceries")
    print("5. Switch Family")
    print("6. Exit")

# ===== EVENTS =====
def add_event():
    family = get_family_data()
    date = input("Event date (YYYY-MM-DD): ").strip()
    text = input("Event description: ").strip()
    if not date or not text:
        print("Invalid input! Event not added.")
        return
    family["events"].append({"date": date, "text": text, "sent": []})
    save_data()
    print("Event added!")
    send_telegram(f"*New Family Event!*\n*Date:* {date}\n*Event:* {text}")

def list_events():
    family = get_family_data()
    today = datetime.today()
    if not family["events"]:
        print("No events yet.")
        return
    for i, e in enumerate(family["events"], 1):
        try:
            ed = datetime.strptime(e["date"], "%Y-%m-%d")
        except ValueError:
            continue
        diff = (ed - today).days
        status = f"in {diff} day(s)" if diff > 0 else "Elapsed"
        print(f"{i}. {e['date']} - {e['text']} ({status})")

def remove_event():
    family = get_family_data()
    list_events()
    if not family["events"]:
        return
    try:
        i = int(input("Enter event number to remove: ")) - 1
        removed = family["events"].pop(i)
        save_data()
        print(f"Removed: {removed['text']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== CHORES =====
def add_chore():
    family = get_family_data()
    name = input("Chore name: ").strip()
    person = input("Assigned to: ").strip()
    if not name or not person:
        print("Invalid input! Chore not added.")
        return
    family["chores"].append({"name": name, "person": person, "done": False})
    save_data()
    print("Chore added!")
    send_telegram(f"*New Chore Assigned!*\n*Person:* {person}\n*Chore:* {name}")

def list_chores():
    family = get_family_data()
    if not family["chores"]:
        print("No chores yet.")
        return
    for i, c in enumerate(family["chores"], 1):
        status = "Done" if c["done"] else "Pending"
        print(f"{i}. {c['name']} - {c['person']} ({status})")

def mark_chore_done():
    family = get_family_data()
    list_chores()
    if not family["chores"]:
        return
    try:
        i = int(input("Enter chore number to mark done: ")) - 1
        family["chores"][i]["done"] = True
        save_data()
        print("Chore marked as done!")
    except (ValueError, IndexError):
        print("Invalid selection!")

def remove_chore():
    family = get_family_data()
    list_chores()
    if not family["chores"]:
        return
    try:
        i = int(input("Enter chore number to remove: ")) - 1
        removed = family["chores"].pop(i)
        save_data()
        print(f"Removed: {removed['name']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== BILLS =====
def add_bill():
    family = get_family_data()
    name = input("Bill name: ").strip()
    date = input("Due date (YYYY-MM-DD): ").strip()
    if not name or not date:
        print("Invalid input! Bill not added.")
        return
    family["bills"].append({"name": name, "date": date, "sent": []})
    save_data()
    print("Bill added!")
    send_telegram(f"*New Bill Due!*\n*Bill:* {name}\n*Due Date:* {date}")

def list_bills():
    family = get_family_data()
    today = datetime.today()
    if not family["bills"]:
        print("No bills yet.")
        return
    for i, b in enumerate(family["bills"], 1):
        try:
            bd = datetime.strptime(b["date"], "%Y-%m-%d")
        except ValueError:
            continue
        diff = (bd - today).days
        status = f"Due in {diff} day(s)" if diff >= 0 else "Elapsed"
        print(f"{i}. {b['name']} - {b['date']} ({status})")

def remove_bill():
    family = get_family_data()
    list_bills()
    if not family["bills"]:
        return
    try:
        i = int(input("Enter bill number to remove: ")) - 1
        removed = family["bills"].pop(i)
        save_data()
        print(f"Removed: {removed['name']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== GROCERIES =====
def add_grocery():
    family = get_family_data()
    name = input("Grocery item name: ").strip()
    date = input("Expiration date (YYYY-MM-DD): ").strip()
    if not name or not date:
        print("Invalid input! Grocery not added.")
        return
    family["groceries"].append({"name": name, "date": date, "sent": []})
    save_data()
    print("Grocery added!")
    send_telegram(f"*New Grocery Added!*\n*Item:* {name}\n*Expires:* {date}")

def list_groceries():
    family = get_family_data()
    today = datetime.today()
    if not family["groceries"]:
        print("No groceries yet.")
        return
    for i, g in enumerate(family["groceries"], 1):
        try:
            gd = datetime.strptime(g["date"], "%Y-%m-%d")
        except ValueError:
            continue
        expired = "Expired" if gd < today else "Fresh"
        print(f"{i}. {g['name']} - Exp: {g['date']} ({expired})")

def remove_grocery():
    family = get_family_data()
    list_groceries()
    if not family["groceries"]:
        return
    try:
        i = int(input("Enter grocery number to remove: ")) - 1
        removed = family["groceries"].pop(i)
        save_data()
        print(f"Removed: {removed['name']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== REMINDERS THREAD =====
def reminders():
    while True:
        if current_family:
            family = get_family_data()
            today = datetime.today()

            # EVENTS
            for e in family["events"]:
                date_str = e.get("date", "")
                if not date_str:
                    continue
                try:
                    ed = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
                diff = (ed - today).days
                if diff >= 0 and diff not in e.get("sent", []):
                    message = f"*Reminder! Family Event*\n*Date:* {date_str}\n*Event:* {e.get('text','')}"
                    send_telegram(message)
                    e.setdefault("sent", []).append(diff)

            # BILLS
            for b in family["bills"]:
                date_str = b.get("date", "")
                if not date_str:
                    continue
                try:
                    bd = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
                diff = (bd - today).days
                for notify_day in [3, 1, 0]:
                    if diff == notify_day and diff not in b.get("sent", []):
                        message = f"*Reminder! Bill Due*\n*Bill:* {b.get('name','')}\n*Due Date:* {date_str}"
                        send_telegram(message)
                        b.setdefault("sent", []).append(diff)

            # GROCERIES
            for g in family["groceries"]:
                date_str = g.get("date", "")
                if not date_str:
                    continue
                try:
                    gd = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
                diff = (gd - today).days
                for notify_day in [2, 1, 0]:
                    if diff == notify_day and diff not in g.get("sent", []):
                        day_text = "today" if diff == 0 else f"in {diff} day(s)"
                        message = f"*Grocery Expiration Reminder*\n*Item:* {g.get('name','')}\n*Expires:* {date_str} ({day_text})"
                        send_telegram(message)
                        g.setdefault("sent", []).append(diff)

            save_data()
        time.sleep(REMINDER_INTERVAL)

# ===== MAIN LOOP =====
def main():
    load_data()
    input_family()
    input_chat_id()

    # Start reminders thread
    t = threading.Thread(target=reminders, daemon=True)
    t.start()

    while True:
        print_menu()
        choice = input("Select option: ").strip()
        if choice == "1":
            while True:
                print("\n--- EVENTS ---")
                list_events()
                print("a. Add  r. Remove  b. Back")
                cmd = input("Choose: ").strip().lower()
                if cmd == "a":
                    add_event()
                elif cmd == "r":
                    remove_event()
                elif cmd == "b":
                    break
        elif choice == "2":
            while True:
                print("\n--- CHORES ---")
                list_chores()
                print("a. Add  d. Done  r. Remove  b. Back")
                cmd = input("Choose: ").strip().lower()
                if cmd == "a":
                    add_chore()
                elif cmd == "d":
                    mark_chore_done()
                elif cmd == "r":
                    remove_chore()
                elif cmd == "b":
                    break
        elif choice == "3":
            while True:
                print("\n--- BILLS ---")
                list_bills()
                print("a. Add  r. Remove  b. Back")
                cmd = input("Choose: ").strip().lower()
                if cmd == "a":
                    add_bill()
                elif cmd == "r":
                    remove_bill()
                elif cmd == "b":
                    break
        elif choice == "4":
            while True:
                print("\n--- GROCERIES ---")
                list_groceries()
                print("a. Add  r. Remove  b. Back")
                cmd = input("Choose: ").strip().lower()
                if cmd == "a":
                    add_grocery()
                elif cmd == "r":
                    remove_grocery()
                elif cmd == "b":
                    break
        elif choice == "5":
            input_family()
        elif choice == "6":
            print("Exiting app. Goodbye!")
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
