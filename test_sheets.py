import toml
import gspread
from google.oauth2.service_account import Credentials

# Load secrets
secrets = toml.load('.streamlit/secrets.toml')

print("Step 1: Secrets loaded OK")
print(f"  Sheet URL: {secrets.get('GOOGLE_SHEET_URL', 'MISSING')}")
sa = secrets.get('gcp_service_account', {})
print(f"  client_email: {sa.get('client_email', 'MISSING')}")

# Authenticate
creds = Credentials.from_service_account_info(
    sa,
    scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
)
client = gspread.authorize(creds)
print("Step 2: Authenticated OK")

# Open sheet
sheet = client.open_by_url(secrets['GOOGLE_SHEET_URL'])
print(f"Step 3: Sheet opened — '{sheet.title}'")

# List tabs
tabs = [ws.title for ws in sheet.worksheets()]
print(f"Step 4: Tabs found: {tabs}")

# Check
if "Reviews" in tabs:
    print("  OK - 'Reviews' tab found")
else:
    print("  ERROR - 'Reviews' tab NOT found")
    print("  Rename one tab to exactly: Reviews")

if "Itineraries" in tabs:
    print("  OK - 'Itineraries' tab found")
else:
    print("  ERROR - 'Itineraries' tab NOT found")
    print("  Rename one tab to exactly: Itineraries")