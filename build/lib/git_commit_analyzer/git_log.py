import subprocess
import re

def get_git_log(start_date=None, end_date=None):
    pretty_format = "%H|%an|%ae|%ad"
    command = ["git", "log", f"--pretty=format:{pretty_format}", "--date=iso", "--numstat"]
    if start_date:
        command.extend(["--since", start_date])
    if end_date:
        command.extend(["--until", end_date])
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def parse_git_log(log, user_db, debug=False):
    commits = []
    current_commit = None
    for line in log.splitlines():
        if re.match(r"^[a-f0-9]{40}", line):
            if current_commit:
                commits.append(current_commit)
            parts = line.split('|')
            commit_hash = parts[0]
            author_name = parts[1]
            author_email = parts[2]
            timestamp = parts[3]
            main_email, full_name = get_main_email_and_name(author_email, author_name, user_db)
            author_full = full_name
            current_commit = {
                "commit_hash": commit_hash,
                "author_full": author_full,
                "timestamp": timestamp,
                "lines_added": 0,
                "lines_removed": 0
            }
            if debug:
                print(f"hash {commit_hash}")
                print(f"author_name {author_name}")
                print(f"author_email {author_email}")
                print(f"timestamp {timestamp}")
                print(f"main_email {main_email}")
                print(f"author_full {author_full}")
        elif re.match(r"^\d+\s+\d+", line):
            added, removed, _ = line.split(maxsplit=2)
            current_commit["lines_added"] += int(added)
            current_commit["lines_removed"] += int(removed)
    if current_commit:
        commits.append(current_commit)
    return commits

def get_main_email_and_name(email, username, user_db):
    for user in user_db["users"]:
        if email == user["email"] or email in user["alternate_emails"] or username in user["alternate_user_names"]:
            return user["email"], user["full_name"]
    return email, username
