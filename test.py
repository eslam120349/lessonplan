import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

print("=" * 70)
print("🔍 Testing Supabase API Connection")
print("=" * 70)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

print(f"\n📋 Configuration:")
print(f"   URL: {SUPABASE_URL}")
print(f"   Key: {SUPABASE_KEY[:30]}...")

# Test 1: Check key type
if SUPABASE_KEY.startswith("sb_publishable_"):
    print("\n❌ WARNING: You're using 'sb_publishable_' key!")
    print("   This might not work with all libraries.")
    print("   Use 'Anon Key (Legacy)' instead (starts with 'eyJ...')")
elif SUPABASE_KEY.startswith("eyJ"):
    print("\n✅ Using correct Anon Key (JWT)")
else:
    print("\n⚠️  Unknown key format")

# Test 2: Try to connect
print("\n🔌 Testing Supabase client...")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created successfully")
    
    # Test 3: Try a simple query
    print("\n🔍 Testing database access...")
    try:
        # Try to access auth users (this should work with anon key)
        response = supabase.auth.get_session()
        print("✅ Supabase API is accessible!")
        
    except Exception as e:
        print(f"⚠️  API test: {str(e)[:100]}")
        
except Exception as e:
    print(f"❌ Failed to create client: {e}")

print("\n" + "=" * 70)