import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from weekly_audit import WeeklyAudit

audit = WeeklyAudit()
audit.run_audit()