import json
import os

USER_DB_PATH = os.path.expanduser("~/etc/users.json")

def load_user_db():
    if not os.path.exists(USER_DB_PATH):
        return {"users": []}
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def save_user_db(db):
    os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
    with open(USER_DB_PATH, "w") as f:
        json.dump(db, f, indent=4)

def add_or_update_user(email, full_name=None, alternate_user_names=None, alternate_emails=None, team=None):
    db = load_user_db()
    user_exists = False
    for user in db["users"]:
        if user["email"] == email:
            user_exists = True
            if full_name:
                user["full_name"] = full_name
            if alternate_user_names:
                user["alternate_user_names"] = alternate_user_names
            if alternate_emails:
                user["alternate_emails"] = alternate_emails
            if team:
                user["team"] = team
            break
    if not user_exists:
        user = {
            "email": email,
            "full_name": full_name,
            "alternate_user_names": alternate_user_names or [],
            "alternate_emails": alternate_emails or [],
            "team": team
        }
        db["users"].append(user)
    save_user_db(db)
    print(f"Added/Updated user: {full_name} with email {email}")
