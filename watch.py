import subprocess
import time
import os
import argparse

parser = argparse.ArgumentParser(description="watch a file and restart it on changes")
parser.add_argument("file", help="the file to watch and execute")
args = parser.parse_args()

watched_file = args.file
last_mtime = None
process = None

def run_script():
    global process
    if process:
        process.terminate()
    print(f"\n🔁 running {watched_file}...\n")
    process = subprocess.Popen(["python", watched_file])

while True:
    try:
        mtime = os.path.getmtime(watched_file)
        if mtime != last_mtime:
            last_mtime = mtime
            run_script()
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n👋 stopping watcher.")
        if process:
            process.terminate()
        break
