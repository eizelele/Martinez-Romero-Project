from datetime import datetime


'''
===== TWILIO SETTINGS =====
'''
account_sid = 'ACcfb25e2c39f10ff1fa59a72a67408cd4'
auth_token = 'fc4e92c9ecf60b4245b3c6d886643b64'
twilio_number = '+14352203434'

client = Client(account_sid, auth_token)

def send_sms(to_number, message):
    """Send SMS using Twilio"""
    try:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=to_number
        )
        print(f" SMS sent to {to_number}")
    except Exception as e:
        print(f" Could not send SMS: {e}")

# ===== DATA =====
data = {
    "family": "",
    "chores": [],
    "events": [],
    "bills": [],
    "groceries": []
}

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
    print(f"Welcome, {name} Family")

# ===== EVENTS =====
def add_event():
    date = input("Event date (YYYY-MM-DD): ").strip()
    text = input("Event description: ").strip()
    phone = input("Enter phone number to notify (+639XXXXXXXXX): ").strip()

    data["events"].append({"date": date, "text": text})
    print("Event added!")

    message = f"Hi! New family event on {date}: {text}"
    send_sms(phone, message)

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
        print(f"Removed: {removed['text']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== CHORES =====
def add_chore():
    name = input("Chore name: ").strip()
    person = input("Assigned to: ").strip()
    phone = input("Enter phone number to notify (+639XXXXXXXXX): ").strip()

    data["chores"].append({"name": name, "person": person, "done": False})
    print("Chore added!")

    message = f"Hi {person}, you have a new chore: {name}"
    send_sms(phone, message)

def list_chores():
    if not data["chores"]:
        print("No chores yet.")
        return
    for i, c in enumerate(data["chores"], 1):
        status = "Done" if c["done"] else " Pending"
        print(f"{i}. {c['name']} - {c['person']} ({status})")

def mark_chore_done():
    list_chores()
    if not data["chores"]:
        return
    try:
        i = int(input("Enter chore number to mark done: ")) - 1
        data["chores"][i]["done"] = True
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
        print(f"Removed: {removed['name']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== BILLS =====
def add_bill():
    name = input("Bill name: ").strip()
    date = input("Due date (YYYY-MM-DD): ").strip()
    phone = input("Enter phone number to notify (+639XXXXXXXXX): ").strip()

    data["bills"].append({"name": name, "date": date})
    print("Bill added!")

    message = f"Hi! New bill due on {date}: {name}"
    send_sms(phone, message)

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
        print(f"Removed: {removed['name']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== GROCERIES =====
def add_grocery():
    name = input("Grocery item name: ").strip()
    date = input("Expiration date (YYYY-MM-DD): ").strip()
    data["groceries"].append({"name": name, "date": date})
    print("Grocery added!")

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
        print(f"Removed: {removed['name']}")
    except (ValueError, IndexError):
        print("Invalid selection!")

# ===== MAIN LOOP =====
def main():
    input_family()
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


