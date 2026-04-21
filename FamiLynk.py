
from datetime import datetime, timedelta
import requests, json, os, threading, time

TOKEN = "8712367782:AAGm-0SGpYlRWZbPhLaKLGbbw-LHWwHS4I0"
DATA_FILE = "data.json"

CHAT_ID = ""
data = {}
current_user = None

# ===== TELEGRAM =====
def send_telegram(msg):
    if not CHAT_ID:
        print("⚠️ No chat ID")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        )
        print("✅ Sent!")
    except Exception as e:
        print("❌", e)

# ===== DATA =====
def load_data():
    global data
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {"users": {}}

    if "users" not in data:
        data["users"] = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===== USER =====
def input_user():
    global current_user
    name = input("Enter user name: ").strip()
    while not name:
        name = input("Enter user name: ").strip()
        
    if name not in data["users"]:
        data["users"][name] = {
            "events": [],
            "chores": [],
            "bills": [],
            "groceries": []
        }

    current_user = name
    print(f"👋 Welcome, {name}!")

def input_chat():
    global CHAT_ID
    CHAT_ID = input("Enter chat ID: ").strip()
    print("✅ Saved!")

# ===== DATE PARSER =====
def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except:
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except:
            return None

# ===== REMINDERS =====
def reminders_loop():
    while True:
        try:
            if not current_user:
                time.sleep(5)
                continue

            usr = data["users"][current_user]
            now = datetime.now()

            # EVENTS (daily reminder)
            for e in usr["events"]:
                dt = parse_date(e.get("datetime") or e.get("date"))
                if not dt:
                    continue

                days = (dt.date() - now.date()).days
                if days >= 0:
                    key = f"sent_{now.date()}"
                    if not e.get(key):
                        send_telegram(f"📅 *Event*\n{e['text']}\n{dt.strftime('%b %d %I:%M %p')}")
                        e[key] = True

            # BILLS
            for b in usr["bills"]:
                dt = parse_date(b.get("date"))
                if not dt:
                    continue

                days = (dt.date() - now.date()).days
                for d in [3,1,0]:
                    key = f"sent_{d}"
                    if days == d and not b.get(key):
                        send_telegram(f"💸 *Bill*\n{b['name']} due in {d} day(s)")
                        b[key] = True

            # GROCERIES
            for g in usr["groceries"]:
                dt = parse_date(g.get("date"))
                if not dt:
                    continue

                days = (dt.date() - now.date()).days
                for d in [2,1,0]:
                    key = f"sent_{d}"
                    if days == d and not g.get(key):
                        send_telegram(f"🥦 *Expiring*\n{g['name']} in {d} day(s)")
                        g[key] = True

            save_data()
            time.sleep(30)

        except Exception as e:
            print("⚠️ Reminder error:", e)
            time.sleep(5)

# ===== EVENTS =====
def events_menu():
    usr = data["users"][current_user]

    while True:
        print("\n--- EVENTS ---")
        for i,e in enumerate(usr["events"],1):
            print(f"{i}. {e['text']} - {e.get('datetime')}")

        print("a add | r remove | e edit | b back")
        c = input(">> ")

        if c == "a":
            d = input("Date (YYYY-MM-DD HH:MM): ")
            dt = parse_date(d)
            if not dt or dt < datetime.now():
                print("❌ Invalid/past date")
                continue

            txt = input("Event: ")
            usr["events"].append({"datetime": d, "text": txt})
            save_data()
            send_telegram(f"📅 *New Event*\n{txt}\n{dt.strftime('%b %d %I:%M %p')}")

        elif c == "r":
            i = int(input("num: ")) - 1
            usr["events"].pop(i)
            save_data()

        elif c == "e":
            i = int(input("num: ")) - 1
            ev = usr["events"][i]

            print(f"Editing: {ev['text']} - {ev.get('datetime')}")
            new_text = input("New text (enter skip): ")
            new_date = input("New date YYYY-MM-DD HH:MM (enter skip): ")

            if new_text:
                ev["text"] = new_text

            if new_date:
                dt = parse_date(new_date)
                if dt and dt >= datetime.now():
                    ev["datetime"] = new_date
                else:
                    print("❌ Invalid date")

            save_data()
            print("✅ Updated!")

        elif c == "b":
            break

# ===== CHORES =====
def chores_menu():
    usr = data["users"][current_user]

    while True:
        print("\n--- CHORES ---")
        for i,c in enumerate(usr["chores"],1):
            print(f"{i}. {c['name']} {'✅' if c['done'] else '❌'}")

        print("a add | d done | r remove | b back")
        c = input(">> ")

        if c == "a":
            name = input("Chore: ")
            usr["chores"].append({"name": name, "done": False})
            save_data()
            send_telegram(f"🧹 *New Chore*\n{name}")

        elif c == "d":
            i = int(input("num: ")) - 1
            usr["chores"][i]["done"] = True
            save_data()

        elif c == "r":
            i = int(input("num: ")) - 1
            usr["chores"].pop(i)
            save_data()

        elif c == "b":
            break

# ===== BILLS =====
def bills_menu():
    usr = data["users"][current_user]

    while True:
        print("\n--- BILLS ---")
        for i,b in enumerate(usr["bills"],1):
            print(f"{i}. {b['name']} - {b['date']}")

        print("a add | r remove | e edit | b back")
        c = input(">> ")

        if c == "a":
            d = input("Date (YYYY-MM-DD): ")
            if not parse_date(d):
                print("❌ Invalid")
                continue

            name = input("Bill: ")
            usr["bills"].append({"date": d, "name": name})
            save_data()
            send_telegram(f"💸 *New Bill*\n{name}\nDue: {d}")

        elif c == "r":
            i = int(input("num: ")) - 1
            usr["bills"].pop(i)
            save_data()

        elif c == "e":
            i = int(input("num: ")) - 1
            b = usr["bills"][i]

            name = input("New name (enter skip): ")
            date = input("New date YYYY-MM-DD (enter skip): ")

            if name:
                b["name"] = name
            if date and parse_date(date):
                b["date"] = date

            save_data()
            print("✅ Updated!")

        elif c == "b":
            break

# ===== GROCERIES =====
def groceries_menu():
    usr = data["users"][current_user]

    while True:
        print("\n--- GROCERIES ---")
        for i,g in enumerate(usr["groceries"],1):
            print(f"{i}. {g['name']} - {g['date']}")

        print("a add | r remove | e edit | b back")
        c = input(">> ")

        if c == "a":
            d = input("Date (YYYY-MM-DD): ")
            if not parse_date(d):
                print("❌ Invalid")
                continue

            name = input("Item: ")
            usr["groceries"].append({"date": d, "name": name})
            save_data()
            send_telegram(f"🥦 *New Grocery*\n{name}\nExpires: {d}")

        elif c == "r":
            i = int(input("num: ")) - 1
            usr["groceries"].pop(i)
            save_data()

        elif c == "e":
            i = int(input("num: ")) - 1
            g = usr["groceries"][i]

            name = input("New name (enter skip): ")
            date = input("New date YYYY-MM-DD (enter skip): ")

            if name:
                g["name"] = name
            if date and parse_date(date):
                g["date"] = date

            save_data()
            print("✅ Updated!")

        elif c == "b":
            break

# ===== MAIN =====
def main():
    load_data()
    input_user()
    input_chat()

    threading.Thread(target=reminders_loop, daemon=True).start()

    while True:
        print("\n1 Events\n2 Chores\n3 Bills\n4 Groceries\n5 Switch User\n6 Exit")
        c = input(">> ")

        if c == "1":
            events_menu()
        elif c == "2":
            chores_menu()
        elif c == "3":
            bills_menu()
        elif c == "4":
            groceries_menu()
        elif c == "5":
            input_user()
        elif c == "6":
            break

if __name__ == "__main__":
    main()
