# git_commit_analyzer/analyzer.py

import argparse
import pandas as pd
from .git_log import get_git_log, parse_git_log
from .user_db import load_user_db, add_or_update_user

def analyze_commits(commits, team=None, user_db=None):
    if not commits:
        print("No commits found.")
        return pd.DataFrame()

    df = pd.DataFrame(commits)

    if 'author_full' not in df.columns:
        print("Column 'author_full' not found in DataFrame. DataFrame columns are:", df.columns)
        return pd.DataFrame()

    if team:
        team_users = {user["full_name"] for user in user_db["users"] if user.get("team", "").lower() == team.lower()}
        df = df[df['author_full'].isin(team_users)]

    summary = df.groupby('author_full').agg({
        'commit_hash': 'count',
        'lines_added': 'sum',
        'lines_removed': 'sum'
    }).rename(columns={'commit_hash': 'commits'}).reset_index().rename(columns={'author_full': 'Author'})

    # Calculate percentages
    total_commits = summary['commits'].sum()
    total_lines_added = summary['lines_added'].sum()
    summary['%_commits'] = (summary['commits'] / total_commits * 100).round(2)
    summary['%_lines_added'] = (summary['lines_added'] / total_lines_added * 100).round(2)

    # Add totals row
    totals = {
        'Author': 'TOTAL',
        'commits': total_commits,
        'lines_added': total_lines_added,
        'lines_removed': summary['lines_removed'].sum(),
        '%_commits': 100.00,
        '%_lines_added': 100.00
    }

    summary = pd.concat([summary, pd.DataFrame([totals])], ignore_index=True)
    return summary

def main():
    parser = argparse.ArgumentParser(description='Analyze git commit distribution.')
    parser.add_argument('--sort-by', type=str, default='commits', help='Column to sort by (default: commits)')
    parser.add_argument('--extra-user-info', action='store_true', help='Include GitHub username as an additional column')
    parser.add_argument('--add-user', action='store_true', help='Add or update a user in the database')
    parser.add_argument('--email', type=str, help='Email of the user')
    parser.add_argument('--full-name', type=str, help='Full name of the user')
    parser.add_argument('--alternate-user', type=str, help='Comma-separated list of alternate usernames')
    parser.add_argument('--alternate-email', type=str, help='Comma-separated list of alternate emails')
    parser.add_argument('--team', type=str, help='Team of the user')
    parser.add_argument('--debug', action='store_true', help='Print debug information')
    parser.add_argument('--since', type=str, dest='start_date', help='Start date for filtering commits (YYYY-MM-DD)')
    parser.add_argument('--until', type=str, dest='end_date', help='End date for filtering commits (YYYY-MM-DD)')
    args = parser.parse_args()

    if args.add_user:
        if not args.email or not args.full_name:
            parser.error("--email and --full-name are required when using --add-user")
        alternate_user_names = args.alternate_user.split(',') if args.alternate_user else []
        alternate_emails = args.alternate_email.split(',') if args.alternate_email else []
        add_or_update_user(
            email=args.email,
            full_name=args.full_name,
            alternate_user_names=alternate_user_names,
            alternate_emails=alternate_emails,
            team=args.team
        )
        return

    user_db = load_user_db()
    log = get_git_log(start_date=args.start_date, end_date=args.end_date)
    commits = parse_git_log(log, user_db, debug=args.debug)

    if args.debug:
        print("Commits parsed:", commits)

    summary = analyze_commits(commits, team=args.team, user_db=user_db)

    if summary.empty:
        print("No summary available.")
        return

    # Extract the totals row before sorting
    totals = summary[summary['Author'] == 'TOTAL']
    summary = summary[summary['Author'] != 'TOTAL']

    # Sort by the specified column
    if args.sort_by in summary.columns:
        summary = summary.sort_values(by=args.sort_by, ascending=False)

    # Append the totals row back to the bottom
    summary = pd.concat([summary, totals], ignore_index=True)

    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
