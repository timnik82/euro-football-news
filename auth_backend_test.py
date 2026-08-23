#!/usr/bin/env python3
"""
Backend Authentication Testing Script
Tests both email/password and Google OAuth session flows
"""
import requests
import sys
import json
from datetime import datetime

class AuthTester:
    def __init__(self, base_url="https://euro-football-kid.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = []
        
    def log(self, message, level="INFO"):
        """Log test messages"""
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️"
        }.get(level, "•")
        print(f"{prefix} {message}")
    
    def test_email_password_login(self):
        """Test 1: POST /api/auth/login with admin credentials"""
        self.tests_run += 1
        self.log("Test 1: Email/Password Login (admin@example.com)", "INFO")
        
        try:
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json={"email": "admin@example.com", "password": "admin123"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == "admin@example.com":
                    self.tests_passed += 1
                    self.log(f"Login successful - User: {data.get('name')} ({data.get('email')})", "SUCCESS")
                    self.log(f"   Auth provider: {data.get('auth_provider', 'N/A')}", "INFO")
                    self.log(f"   Role: {data.get('role', 'N/A')}", "INFO")
                    
                    # Check cookies
                    cookies = self.session.cookies.get_dict()
                    if 'access_token' in cookies or 'session_token' in cookies:
                        self.log(f"   Cookies set: {list(cookies.keys())}", "INFO")
                    return True
                else:
                    self.tests_failed.append("Login returned wrong user")
                    self.log(f"Login returned wrong user: {data.get('email')}", "FAIL")
                    return False
            else:
                self.tests_failed.append(f"Login failed with status {response.status_code}")
                self.log(f"Login failed - Status: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text[:200]}", "FAIL")
                return False
                
        except Exception as e:
            self.tests_failed.append(f"Login exception: {str(e)}")
            self.log(f"Exception during login: {str(e)}", "FAIL")
            return False
    
    def test_auth_me_with_cookie(self):
        """Test 2: GET /api/auth/me using session cookie"""
        self.tests_run += 1
        self.log("Test 2: GET /api/auth/me (using cookie from login)", "INFO")
        
        try:
            response = self.session.get(f"{self.api_url}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("email"):
                    self.tests_passed += 1
                    self.log(f"Auth verification successful - User: {data.get('email')}", "SUCCESS")
                    self.log(f"   User ID: {data.get('user_id', 'N/A')}", "INFO")
                    return True
                else:
                    self.tests_failed.append("/auth/me returned no email")
                    self.log("/auth/me returned incomplete user data", "FAIL")
                    return False
            else:
                self.tests_failed.append(f"/auth/me failed with status {response.status_code}")
                self.log(f"/auth/me failed - Status: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text[:200]}", "FAIL")
                return False
                
        except Exception as e:
            self.tests_failed.append(f"/auth/me exception: {str(e)}")
            self.log(f"Exception during /auth/me: {str(e)}", "FAIL")
            return False
    
    def test_auth_me_with_bearer_token(self, session_token):
        """Test 3: GET /api/auth/me using Bearer token (Google-style session)"""
        self.tests_run += 1
        self.log(f"Test 3: GET /api/auth/me with Bearer token", "INFO")
        
        try:
            # Create new session without cookies
            test_session = requests.Session()
            response = test_session.get(
                f"{self.api_url}/auth/me",
                headers={"Authorization": f"Bearer {session_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("email"):
                    self.tests_passed += 1
                    self.log(f"Bearer auth successful - User: {data.get('email')}", "SUCCESS")
                    self.log(f"   User ID: {data.get('user_id', 'N/A')}", "INFO")
                    return True
                else:
                    self.tests_failed.append("Bearer auth returned no email")
                    self.log("Bearer auth returned incomplete user data", "FAIL")
                    return False
            else:
                self.tests_failed.append(f"Bearer auth failed with status {response.status_code}")
                self.log(f"Bearer auth failed - Status: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text[:200]}", "FAIL")
                return False
                
        except Exception as e:
            self.tests_failed.append(f"Bearer auth exception: {str(e)}")
            self.log(f"Exception during Bearer auth: {str(e)}", "FAIL")
            return False
    
    def test_google_session_invalid(self):
        """Test 4: POST /api/auth/google/session with invalid session_id"""
        self.tests_run += 1
        self.log("Test 4: Google session with invalid session_id", "INFO")
        
        try:
            test_session = requests.Session()
            response = test_session.post(
                f"{self.api_url}/auth/google/session",
                json={"session_id": "invalid_session_12345"},
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 401 or 502, NOT 500
            if response.status_code in [401, 502]:
                self.tests_passed += 1
                self.log(f"Correctly rejected invalid session - Status: {response.status_code}", "SUCCESS")
                try:
                    error_data = response.json()
                    self.log(f"   Error message: {error_data.get('detail', 'N/A')}", "INFO")
                except:
                    pass
                return True
            elif response.status_code == 500:
                self.tests_failed.append("Invalid session returned 500 (should be 401/502)")
                self.log("Invalid session returned 500 Internal Server Error", "FAIL")
                self.log("   Expected: 401 or 502 with proper error message", "FAIL")
                self.log(f"   Response: {response.text[:200]}", "FAIL")
                return False
            else:
                self.tests_failed.append(f"Unexpected status {response.status_code} for invalid session")
                self.log(f"Unexpected status code: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text[:200]}", "FAIL")
                return False
                
        except Exception as e:
            self.tests_failed.append(f"Invalid session test exception: {str(e)}")
            self.log(f"Exception during invalid session test: {str(e)}", "FAIL")
            return False
    
    def test_logout(self):
        """Test 5: POST /api/auth/logout"""
        self.tests_run += 1
        self.log("Test 5: Logout", "INFO")
        
        try:
            response = self.session.post(f"{self.api_url}/auth/logout")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message"):
                    self.tests_passed += 1
                    self.log(f"Logout successful - {data.get('message')}", "SUCCESS")
                    
                    # Verify cookies are cleared
                    cookies = self.session.cookies.get_dict()
                    if not cookies or all(not v for v in cookies.values()):
                        self.log("   Cookies cleared successfully", "INFO")
                    return True
                else:
                    self.tests_failed.append("Logout returned no message")
                    self.log("Logout returned unexpected response", "FAIL")
                    return False
            else:
                self.tests_failed.append(f"Logout failed with status {response.status_code}")
                self.log(f"Logout failed - Status: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text[:200]}", "FAIL")
                return False
                
        except Exception as e:
            self.tests_failed.append(f"Logout exception: {str(e)}")
            self.log(f"Exception during logout: {str(e)}", "FAIL")
            return False
    
    def test_auth_me_after_logout(self):
        """Test 6: Verify /api/auth/me fails after logout"""
        self.tests_run += 1
        self.log("Test 6: Verify auth fails after logout", "INFO")
        
        try:
            response = self.session.get(f"{self.api_url}/auth/me")
            
            if response.status_code == 401:
                self.tests_passed += 1
                self.log("Correctly rejected unauthenticated request", "SUCCESS")
                return True
            elif response.status_code == 200:
                self.tests_failed.append("Auth still valid after logout")
                self.log("Auth still valid after logout (should be 401)", "FAIL")
                return False
            else:
                self.tests_failed.append(f"Unexpected status {response.status_code} after logout")
                self.log(f"Unexpected status: {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.tests_failed.append(f"Post-logout test exception: {str(e)}")
            self.log(f"Exception during post-logout test: {str(e)}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("\n" + "=" * 70)
        print("🔐 BACKEND AUTHENTICATION TESTING")
        print("=" * 70)
        print(f"Backend URL: {self.api_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")
        
        # Test 1: Email/Password Login
        print("📧 EMAIL/PASSWORD AUTHENTICATION")
        print("-" * 70)
        login_success = self.test_email_password_login()
        print()
        
        # Test 2: Auth verification with cookie
        if login_success:
            self.test_auth_me_with_cookie()
            print()
        else:
            self.log("Skipping cookie test (login failed)", "WARN")
            print()
        
        # Test 3: Bearer token auth (using test session)
        print("🔑 GOOGLE OAUTH SESSION AUTHENTICATION")
        print("-" * 70)
        test_session_token = "test_session_7350be54d0a14b14a263e5f23cbb000f"
        self.test_auth_me_with_bearer_token(test_session_token)
        print()
        
        # Test 4: Invalid Google session
        self.test_google_session_invalid()
        print()
        
        # Test 5: Logout
        print("🚪 LOGOUT FLOW")
        print("-" * 70)
        self.test_logout()
        print()
        
        # Test 6: Verify logout worked
        self.test_auth_me_after_logout()
        print()
        
        # Summary
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        
        if self.tests_passed == self.tests_run:
            print("\n✅ ALL TESTS PASSED!")
            success_rate = 100.0
        else:
            success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
            print(f"\n⚠️  Success Rate: {success_rate:.1f}%")
            
            if self.tests_failed:
                print("\n❌ FAILED TESTS:")
                for i, failure in enumerate(self.tests_failed, 1):
                    print(f"   {i}. {failure}")
        
        print("=" * 70 + "\n")
        
        return 0 if success_rate == 100 else 1

def main():
    tester = AuthTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
