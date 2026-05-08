import requests
import sys
import json
from datetime import datetime

class FootballAPITester:
    def __init__(self, base_url="https://young-fan-hub.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=False):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_leagues(self):
        """Test leagues endpoint"""
        success, response = self.run_test(
            "Get Leagues",
            "GET",
            "leagues",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} leagues")
            for league in response[:3]:  # Show first 3
                print(f"   - {league.get('name')} ({league.get('code')})")
        return success

    def test_matches_today(self):
        """Test today's matches"""
        success, response = self.run_test(
            "Get Today's Matches",
            "GET",
            "matches/today",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} matches today")
        return success

    def test_matches_upcoming(self):
        """Test upcoming matches"""
        success, response = self.run_test(
            "Get Upcoming Matches",
            "GET",
            "matches/upcoming",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} upcoming matches")
        return success

    def test_stories(self):
        """Test match stories"""
        success, response = self.run_test(
            "Get Match Stories",
            "GET",
            "stories",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} stories")
        return success

    def test_league_standings(self, league_code="PL"):
        """Test league standings"""
        success, response = self.run_test(
            f"Get {league_code} Standings",
            "GET",
            f"leagues/{league_code}/standings",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} standing groups")
        return success

    def test_league_scorers(self, league_code="PL"):
        """Test league top scorers"""
        success, response = self.run_test(
            f"Get {league_code} Top Scorers",
            "GET",
            f"leagues/{league_code}/scorers",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} top scorers")
        return success

    def test_league_matches(self, league_code="PL"):
        """Test league matches"""
        success, response = self.run_test(
            f"Get {league_code} Matches",
            "GET",
            f"leagues/{league_code}/matches",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} matches")
        return success

    def test_auth_register(self):
        """Test user registration"""
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={"name": "Test User", "email": test_email, "password": "test123"}
        )
        if success:
            self.test_user_email = test_email
            print(f"   Registered user: {test_email}")
        return success

    def test_auth_login(self):
        """Test user login with admin credentials"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@example.com", "password": "admin123"}
        )
        if success:
            print(f"   Logged in as: {response.get('email')}")
        return success

    def test_auth_me(self):
        """Test get current user"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        if success:
            print(f"   Current user: {response.get('email')}")
        return success

    def test_favorites_get(self):
        """Test get favorites (requires auth)"""
        success, response = self.run_test(
            "Get Favorites",
            "GET",
            "favorites",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} favorites")
        return success

    def test_favorites_toggle(self):
        """Test toggle favorite"""
        success, response = self.run_test(
            "Toggle Favorite League",
            "POST",
            "favorites",
            200,
            data={"type": "league", "item_id": "PL", "name": "Premier League", "crest": ""}
        )
        if success:
            print(f"   Action: {response.get('action')}")
        return success

def main():
    print("🚀 Starting Football PWA Backend API Tests")
    print("=" * 50)
    
    tester = FootballAPITester()
    
    # Test public endpoints first
    print("\n📊 Testing Public Endpoints")
    print("-" * 30)
    
    tester.test_leagues()
    tester.test_matches_today()
    tester.test_matches_upcoming()
    tester.test_stories()
    
    # Test league-specific endpoints
    print("\n🏆 Testing League Endpoints")
    print("-" * 30)
    
    tester.test_league_standings("PL")
    tester.test_league_scorers("PL")
    tester.test_league_matches("PL")
    
    # Test different leagues
    for league in ["CL", "PD", "SA"]:
        tester.test_league_standings(league)
    
    # Test auth endpoints
    print("\n🔐 Testing Auth Endpoints")
    print("-" * 30)
    
    tester.test_auth_register()
    tester.test_auth_login()
    tester.test_auth_me()
    
    # Test favorites (requires auth)
    print("\n❤️ Testing Favorites Endpoints")
    print("-" * 30)
    
    tester.test_favorites_get()
    tester.test_favorites_toggle()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Backend APIs are working well!")
        return 0
    else:
        print("❌ Some backend APIs need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())