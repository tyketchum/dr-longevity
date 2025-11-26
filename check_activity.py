from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Query activities from 11-25-2025
response = supabase.table('activities').select('*').gte('date', '2025-11-25').lte('date', '2025-11-26').order('date', desc=True).execute()

print(f"Found {len(response.data)} activities on 2025-11-25:")
for act in response.data:
    print(f"\nActivity: {act.get('name', 'Unknown')}")
    print(f"  Date: {act.get('date')}")
    print(f"  Duration: {act.get('duration_minutes')} min")
    print(f"  Avg HR: {act.get('avg_hr')}")
    print(f"  Avg Power: {act.get('avg_power')}")
    print(f"  Max Power: {act.get('max_power')}")
    print(f"  Activity Type: {act.get('activity_type')}")
