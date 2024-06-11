import pandas as pd

def highlight(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

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

def print_summary(summary):
    if summary.empty:
        print("No summary available.")
        return

    header = summary.columns.tolist()
    highlighted_header = [highlight(col, '1;32') for col in header]
    summary.columns = highlighted_header

    highlighted_summary = summary.copy()
    highlighted_summary['Author'] = highlighted_summary['Author'].apply(lambda x: highlight(x, '1;34'))

    print(highlighted_summary.to_string(index=False))
