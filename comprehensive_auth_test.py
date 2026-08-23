#!/usr/bin/env python3
"""
Final comprehensive auth test covering all requirements from review request
"""
import requests
import sys

BASE_URL = "https://euro-football-kid.preview.emergentagent.com"
API_URL = f"{BASE_URL}/api"

def test_requirement_1():
    """POST /api/auth/login с admin@example.com / admin123 и затем GET /api/auth/me по cookie"""
    print("\n" + "="*70)
    print("TEST 1: Email/Password Login + Cookie Auth")
    print("="*70)
    
    session = requests.Session()
    
    # Login
    print("→ POST /api/auth/login (admin@example.com / admin123)")
    resp = session.post(f"{API_URL}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.status_code}")
        return False
    
    user = resp.json()
    print(f"✅ Login successful: {user.get('email')}")
    print(f"   Cookies: {list(session.cookies.get_dict().keys())}")
    
    # Get /me with cookie
    print("\n→ GET /api/auth/me (using cookie)")
    resp = session.get(f"{API_URL}/auth/me")
    
    if resp.status_code != 200:
        print(f"❌ /auth/me failed: {resp.status_code}")
        return False
    
    me = resp.json()
    print(f"✅ Auth verified: {me.get('email')}")
    print(f"   User ID: {me.get('user_id')}")
    print(f"   Auth Provider: {me.get('auth_provider')}")
    
    return True

def test_requirement_2():
    """GET /api/auth/me по Bearer session_token для Google-style session"""
    print("\n" + "="*70)
    print("TEST 2: Bearer Token Auth (Google Session)")
    print("="*70)
    
    session_token = "test_session_7350be54d0a14b14a263e5f23cbb000f"
    
    print(f"→ GET /api/auth/me with Bearer {session_token[:30]}...")
    resp = requests.get(f"{API_URL}/auth/me", headers={
        "Authorization": f"Bearer {session_token}"
    })
    
    if resp.status_code != 200:
        print(f"❌ Bearer auth failed: {resp.status_code}")
        print(f"   Response: {resp.text[:200]}")
        return False
    
    me = resp.json()
    print(f"✅ Bearer auth successful: {me.get('email')}")
    print(f"   User ID: {me.get('user_id')}")
    print(f"   Auth Provider: {me.get('auth_provider')}")
    
    return True

def test_requirement_3():
    """POST /api/auth/google/session с невалидным session_id должен вернуть auth-ошибку, а не 500"""
    print("\n" + "="*70)
    print("TEST 3: Invalid Google Session Handling")
    print("="*70)
    
    print("→ POST /api/auth/google/session (invalid session_id)")
    resp = requests.post(f"{API_URL}/auth/google/session", json={
        "session_id": "invalid_test_session_12345"
    })
    
    if resp.status_code == 500:
        print(f"❌ Returned 500 Internal Server Error (should be 401/502)")
        print(f"   Response: {resp.text[:200]}")
        return False
    
    if resp.status_code in [401, 502]:
        print(f"✅ Correctly returned {resp.status_code}")
        try:
            error = resp.json()
            print(f"   Error: {error.get('detail')}")
        except:
            pass
        return True
    
    print(f"⚠️  Unexpected status: {resp.status_code}")
    return False

def test_requirement_4():
    """POST /api/auth/logout должен чистить auth-сессию без серверной ошибки"""
    print("\n" + "="*70)
    print("TEST 4: Logout Without Server Error")
    print("="*70)
    
    session = requests.Session()
    
    # Login first
    print("→ Login first...")
    resp = session.post(f"{API_URL}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.status_code}")
        return False
    
    print("✅ Logged in")
    
    # Logout
    print("\n→ POST /api/auth/logout")
    resp = session.post(f"{API_URL}/auth/logout")
    
    if resp.status_code >= 500:
        print(f"❌ Logout returned server error: {resp.status_code}")
        print(f"   Response: {resp.text[:200]}")
        return False
    
    if resp.status_code == 200:
        print(f"✅ Logout successful (no server error)")
        try:
            msg = resp.json()
            print(f"   Message: {msg.get('message')}")
        except:
            pass
        
        # Verify session cleared
        print("\n→ Verify session cleared...")
        resp = session.get(f"{API_URL}/auth/me")
        if resp.status_code == 401:
            print("✅ Session properly cleared (401 on /auth/me)")
            return True
        else:
            print(f"⚠️  Session still valid: {resp.status_code}")
            return False
    
    print(f"⚠️  Unexpected status: {resp.status_code}")
    return False

def test_requirement_5():
    """Проверка временной тестовой user_session по инструкции"""
    print("\n" + "="*70)
    print("TEST 5: Test Session Data Verification")
    print("="*70)
    
    print("Expected test data:")
    print("  Email: google.test.9a76cd58@example.com")
    print("  User ID: user_ac88620591a3")
    print("  Session Token: test_session_7350be54d0a14b14a263e5f23cbb000f")
    
    session_token = "test_session_7350be54d0a14b14a263e5f23cbb000f"
    
    print(f"\n→ GET /api/auth/me with test session token")
    resp = requests.get(f"{API_URL}/auth/me", headers={
        "Authorization": f"Bearer {session_token}"
    })
    
    if resp.status_code != 200:
        print(f"❌ Failed: {resp.status_code}")
        return False
    
    me = resp.json()
    
    # Verify expected data
    checks = [
        (me.get('email') == 'google.test.9a76cd58@example.com', "Email matches"),
        (me.get('user_id') == 'user_ac88620591a3', "User ID matches"),
        (me.get('auth_provider') == 'google', "Auth provider is Google"),
    ]
    
    all_passed = True
    for passed, desc in checks:
        if passed:
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc}")
            all_passed = False
    
    if all_passed:
        print(f"\n✅ Test session data verified successfully")
        print(f"   Name: {me.get('name')}")
        print(f"   Picture: {me.get('picture', 'N/A')[:50]}...")
    
    return all_passed

def main():
    print("\n" + "="*70)
    print("🔐 COMPREHENSIVE BACKEND AUTH TESTING")
    print("   Based on Review Request Requirements")
    print("="*70)
    print(f"Backend: {API_URL}")
    
    tests = [
        ("Requirement 1: Email/Password + Cookie Auth", test_requirement_1),
        ("Requirement 2: Bearer Token (Google Session)", test_requirement_2),
        ("Requirement 3: Invalid Session Error Handling", test_requirement_3),
        ("Requirement 4: Logout Without Server Error", test_requirement_4),
        ("Requirement 5: Test Session Data", test_requirement_5),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Exception in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed_count}/{total_count} passed")
    
    if passed_count == total_count:
        print("\n✅ ALL REQUIREMENTS VERIFIED - BACKEND AUTH WORKING CORRECTLY")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} requirement(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
