python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
set -e
STATE_FILE="venv/lib/python*/site-packages/discord/state.py"
sed -i "s/self.pending_payments = {int(p\['id'\]): Payment(state=self, data=p) for p in data.get('pending_payments', \[\])}/self.pending_payments = {int(p\['id'\]): Payment(state=self, data=p) for p in (data.get('pending_payments') or [])}/" $STATE_FILE