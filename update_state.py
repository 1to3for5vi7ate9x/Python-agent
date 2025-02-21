import os
import glob
import re

# Find the correct state.py file inside the virtual environment
file_paths = glob.glob("venv/lib/python*/site-packages/discord/state.py")

if not file_paths:
    print("❌ Error: state.py file not found!")
    exit(1)

state_file = file_paths[0]  # Use the first match

try:
    # Read the file
    with open(state_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Define regex pattern to match variations of the line
    pattern = re.compile(r"self\.pending_payments\s*=\s*\{int\(p\['id'\]\):\s*Payment\(state=self,\s*data=p\)\s*for\s*p\s*in\s*data\.get\('pending_payments',\s*\[\]\)\}")

    # Define the replacement line
    new_line = "        self.pending_payments = {int(p['id']): Payment(state=self, data=p) for p in (data.get('pending_payments') or [])}\n"

    # Replace the line using regex
    updated_lines = [new_line if pattern.search(line) else line for line in lines]

    # Write back to the file
    with open(state_file, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

    print(f"✅ Successfully updated {state_file}")

except Exception as e:
    print(f"❌ Error updating {state_file}: {e}")
    exit(1)
