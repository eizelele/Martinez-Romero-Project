from datetime import datetime
import requests
import json
import os

# ===== TELEGRAM SETTINGS =====
TOKEN = "8712367782:AAGm-0SGpYlRWZbPhLaKLGbbw-LHWwHS4I0"  # Replace with your Telegram bot token
CHAT_ID = ""  # Will be set by user input
DATA_FILE = "data.json"

# ===== TELEGRAM FUNCTION =====
def send_telegram(message):
    """Send message using Telegram bot with Markdown formatting"""
    if not CHAT_ID:
        print("No chat ID set! Telegram message not sent.")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data)
        print("Message sent via Telegram")
    except Exception as e:
        print(f"Could not send message: {e}")

# ===== LOAD / SAVE DATA =====
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"family": "", "chores": [], "events": [], "bills": [], "groceries": []}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===== DATA =====
data = load_data()

# ===== HELPERS =====
def print_menu():
    print("\n--- MENU ---")
    print("1. Events")
    print("2. Chores")
    print("3. Bills")
    print("4. Groceries")
    print("5. Change Family / Exit")

def input_family():
    name = input("Enter family name: ").strip()
    while not name:
        print("Family name cannot be empty!")
        name = input("Enter family name: ").strip()
    data["family"] = name
    save_data()
    print(f"\nWelcome, {name} Family!")

def input_chat_id():
    global CHAT_ID
    CHAT_ID = input("Enter your Telegram chat ID: ").strip()
    while not CHAT_ID.isdigit():
        print("Chat ID must be a number!")
        CHAT_ID = input("Enter your Telegram chat ID: ").strip()
    print("Chat ID saved!")

# ===== EVENTS =====
def add_event():
    date = input("Event date (YYYY-MM-DD): ").strip()
    text = input("Event description: ").strip()
    data["events"].append({"date": date, "text": text})
    save_data()
    print("Event added!")
    message = f"*New Family Event!*\n*Date:* {date}\n*Event:* {text}"
    send_telegram(message)

def list_events():
    today = datetime.today()
    if not data["events"]:
        print("No events yet.")
        return
    for i, e in enumerate(data["events"], 1):
        ed = datetime.strptime(e["date"], "%Y-%m-%d")
        diff = (ed - today).days
        status = f"in {diff} day(s)" if diff > 0 else "Elapsed"
        print(f"{i}. {e['date']} - {e['text']} ({status})")

def remove_event():
    list_events()
    if not data["events"]:
        return
    try:
        i = int(input("Enter event number to remove: ")) - 1
        removed = data["events"].pop(i)
        save_data()
        print(f"Removed: {removed['text']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== CHORES =====
def add_chore():
    name = input("Chore name: ").strip()
    person = input("Assigned to: ").strip()
    data["chores"].append({"name": name, "person": person, "done": False})
    save_data()
    print("Chore added!")
    message = f"*New Chore Assigned!*\n*Person:* {person}\n*Chore:* {name}"
    send_telegram(message)

def list_chores():
    if not data["chores"]:
        print("No chores yet.")
        return
    for i, c in enumerate(data["chores"], 1):
        status = "Done" if c["done"] else "Pending"
        print(f"{i}. {c['name']} - {c['person']} ({status})")

def mark_chore_done():
    list_chores()
    if not data["chores"]:
        return
    try:
        i = int(input("Enter chore number to mark done: ")) - 1
        data["chores"][i]["done"] = True
        save_data()
        print("Chore marked as done!")
    except (ValueError, IndexError):
        print("Invalid selection!")

def remove_chore():
    list_chores()
    if not data["chores"]:
        return
    try:
        i = int(input("Enter chore number to remove: ")) - 1
        removed = data["chores"].pop(i)
        save_data()
        print(f"Removed: {removed['name']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== BILLS =====
def add_bill():
    name = input("Bill name: ").strip()
    date = input("Due date (YYYY-MM-DD): ").strip()
    data["bills"].append({"name": name, "date": date})
    save_data()
    print("Bill added!")
    message = f"*New Bill Due!*\n*Bill:* {name}\n*Due Date:* {date}"
    send_telegram(message)

def list_bills():
    today = datetime.today()
    if not data["bills"]:
        print("No bills yet.")
        return
    for i, b in enumerate(data["bills"], 1):
        bd = datetime.strptime(b["date"], "%Y-%m-%d")
        diff = (bd - today).days
        status = f"Due in {diff} day(s)" if diff >= 0 else "Elapsed"
        print(f"{i}. {b['name']} - {b['date']} ({status})")

def remove_bill():
    list_bills()
    if not data["bills"]:
        return
    try:
        i = int(input("Enter bill number to remove: ")) - 1
        removed = data["bills"].pop(i)
        save_data()
        print(f"Removed: {removed['name']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== GROCERIES =====
def add_grocery():
    name = input("Grocery item name: ").strip()
    date = input("Expiration date (YYYY-MM-DD): ").strip()
    data["groceries"].append({"name": name, "date": date})
    save_data()
    print("Grocery added!")
    message = f"*New Grocery Added!*\n*Item:* {name}\n*Expires:* {date}"
    send_telegram(message)

def list_groceries():
    today = datetime.today()
    if not data["groceries"]:
        print("No groceries yet.")
        return
    for i, g in enumerate(data["groceries"], 1):
        expired = "Expired" if datetime.strptime(g["date"], "%Y-%m-%d") < today else "Fresh"
        print(f"{i}. {g['name']} - Exp: {g['date']} ({expired})")

def remove_grocery():
    list_groceries()
    if not data["groceries"]:
        return
    try:
        i = int(input("Enter grocery number to remove: ")) - 1
        removed = data["groceries"].pop(i)
        save_data()
        print(f"Removed: {removed['name']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== MAIN LOOP =====
def main():
    input_family()
    input_chat_id()
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
            print("Exiting app. Goodbye!")
            break

        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
