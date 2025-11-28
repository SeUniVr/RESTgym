import common
import sqlite3
import os
import sys
import shutil
import re



# Collect paths of runs
def collect_runs():
    runs = set()
    api_dirs = os.scandir(f'{common.RESTGYM_BASE_DIR}/results')
    for api_dir in api_dirs:
        if api_dir.is_dir():
            tool_dirs = os.scandir(api_dir)
            for tool_dir in tool_dirs:
                if tool_dir.is_dir():
                    run_dirs = os.scandir(tool_dir)
                    for run_dir in run_dirs:
                        if run_dir.name != '.DS_Store':
                            runs.add(run_dir.path)
    return runs


# Read time budget from file
def parse_time_budget(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Match "Time budget: X minutes." where X is integer
    match = re.search(r'Time budget:\s*(\d+)', content)

    if match:
        minutes = int(match.group(1))
        if minutes > 0:
            return minutes
    return 60


# Count code coverage samples
def count_coverage_samples(run):
    files = os.listdir(f"{run}{common.CODE_COVERAGE_PATH}")
    exec_count = 0
    csv_count = 0
    for file in files:
        if file.endswith('.exec'):
            exec_count += 1
        elif file.endswith('.csv'):
            csv_count += 1
    return exec_count, csv_count

# Perform integrity analysis
def analyze():
    runs = collect_runs()
    print(f"Analyzing {len(runs)} runs.")
    analyzed = {}
    for run in runs:
        # Get time budget for the run
        time_budget = parse_time_budget(f'{run}/time-budget.txt')
        # Init dictionary to store results
        result = {}
        # Verify started.txt exists
        result['started'] = os.path.exists(f"{run}/started.txt")
        # Verify completed.txt exists
        result['completed'] = os.path.exists(f"{run}/completed.txt")
        # Verify database exists
        result['db'] = os.path.exists(f"{run}/{common.DB_FILENAME}")
        # Verify interactions table exists
        if result['db']:
            conn = sqlite3.connect(f"{run}/{common.DB_FILENAME}")
            cursor = conn.cursor()
            result['interactions_table'] = int(cursor.execute("SELECT COUNT(1) FROM sqlite_master WHERE type='table' AND name = 'interactions'").fetchone()[0]) > 0
        else:
            result['interactions_table'] = False
        # Verify at least 130 requests per minute have been sent
        if result['interactions_table']:
            if "genome-nexus" in run and "schemathesis" in run:
                result['requests'] = cursor.execute('SELECT COUNT(1) FROM interactions').fetchone()[0] >= 50 * time_budget
            else:
                result['requests'] = cursor.execute('SELECT COUNT(1) FROM interactions').fetchone()[0] >= 130 * time_budget
        else:
            result['requests'] = False
        # Verify requests span is at least 90% of the time budget
        if result['interactions_table'] and result['requests']:
            result['time_span'] = cursor.execute('SELECT MAX(request_timestamp) - MIN(request_timestamp) FROM interactions').fetchone()[0] >= int(60 * time_budget * 0.9)
        else:
            result['time_span'] = False

        # Verify code coverage dir exists
        result['coverage_dir'] = os.path.exists(f"{run}{common.CODE_COVERAGE_PATH}")
        # Verify all code coverage samples exist
        if result['coverage_dir']:
            exec_count, csv_count = count_coverage_samples(run)
            result['exec_count'] = exec_count >= 12 * time_budget
            result['csv_count'] = csv_count >= 12 * time_budget
            result['exec_csv_match'] = exec_count == csv_count
        else:
            result['exec_count'] = False
            result['csv_count'] = False
            result['exec_csv_match'] = False
        # Add result to returned dictionary
        analyzed[run] = result
        # Print if something is wrong
        for key in result:
            if result[key] == False:
                print(f" => Something wrong in {run}: {result}")
                break
    return analyzed

# Removes runs with problems
def clean(runs):
    for run in runs:
        shutil.rmtree(run, ignore_errors=True)
    print("Removed.")

if __name__ == '__main__':
    common.welcome()
    print("This is the verify_runs module. It will check the integrity of runs.")
    print("[1] Analyze runs")
    print("[2] Analyze runs and remove wrong ones")
    choice = input("Your choice: ")
    if choice != '1' and choice != '2':
        print("Invalid choice!")
        sys.exit(1)
    analyzed = analyze()
    with_problems = []
    for run in analyzed:
        for key in analyzed[run]:
            if analyzed[run][key] == False:
                with_problems.append(run)
                break
    if len(with_problems) == 0:
        print("No runs with problems found.")
    else:
        if choice == '2':
            input(f"Are you sure you want to delete {len(with_problems)}/{len(analyzed)} runs with problems? Press ENTER to continue, or CTRL+C to cancel...")
            clean(with_problems)