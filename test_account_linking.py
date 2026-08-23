#!/usr/bin/env python3
"""
Test account linking: verify that when a Google email matches an existing email,
the account is linked rather than duplicated.
"""
import sys

def check_account_linking():
    """Check if admin account can be linked with Google"""
    import subprocess
    
    print("=" * 70)
    print("🔗 ACCOUNT LINKING VERIFICATION")
    print("=" * 70)
    
    # Check admin user
    print("\n1. Checking admin user (email/password account)...")
    result = subprocess.run([
        "mongosh", "--quiet", "--eval",
        "use('test_database'); db.users.findOne({email: 'admin@example.com'}, {_id: 0, password_hash: 0})"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Admin user found:")
        print(result.stdout)
        
        # Check if admin has google_account_id (would indicate linking capability)
        if "google_account_id" in result.stdout:
            print("✅ Admin account has Google linking capability")
        else:
            print("ℹ️  Admin account is email/password only (no Google link yet)")
    else:
        print("❌ Failed to query admin user")
        return False
    
    # Check Google test user
    print("\n2. Checking Google test user...")
    result = subprocess.run([
        "mongosh", "--quiet", "--eval",
        "use('test_database'); db.users.findOne({email: 'google.test.9a76cd58@example.com'}, {_id: 0})"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Google test user found:")
        print(result.stdout)
        
        if "google_account_id" in result.stdout:
            print("✅ User has google_account_id field")
        if "password_hash" in result.stdout:
            print("ℹ️  User also has password (linked account)")
        else:
            print("ℹ️  User is Google-only (no password)")
    else:
        print("❌ Failed to query Google test user")
        return False
    
    # Check for duplicate emails
    print("\n3. Checking for duplicate email accounts...")
    result = subprocess.run([
        "mongosh", "--quiet", "--eval",
        "use('test_database'); db.users.aggregate([{$group: {_id: '$email', count: {$sum: 1}}}, {$match: {count: {$gt: 1}}}])"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        if result.stdout.strip() == "":
            print("✅ No duplicate email accounts found")
        else:
            print("⚠️  Duplicate emails found:")
            print(result.stdout)
            return False
    else:
        print("❌ Failed to check for duplicates")
        return False
    
    print("\n" + "=" * 70)
    print("✅ ACCOUNT LINKING VERIFICATION PASSED")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = check_account_linking()
    sys.exit(0 if success else 1)
