import requests
import sys
import json
from datetime import datetime

class ClientIntakeAPITester:
    def __init__(self, base_url="https://client-intake-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/")
            success = response.status_code == 200 and "Client Intake API" in response.json().get("message", "")
            self.log_test("API Root", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("API Root", False, str(e))
            return False

    def test_create_submission(self):
        """Test creating a client submission"""
        test_data = {
            "name": "John Doe",
            "business_name": "Test Business Inc",
            "mobile_number": "+1234567890",
            "agreed_to_terms": True
        }
        
        try:
            response = requests.post(f"{self.api_url}/submissions", json=test_data)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Verify all fields are present
                required_fields = ["id", "name", "business_name", "mobile_number", "agreed_to_terms", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Created submission with ID: {data['id']}"
                    self.test_submission_id = data['id']  # Store for later tests
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
            
            self.log_test("Create Submission", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Create Submission", False, str(e))
            return False, {}

    def test_create_submission_without_terms(self):
        """Test creating submission without agreeing to terms (should fail)"""
        test_data = {
            "name": "Jane Doe",
            "business_name": "Another Business",
            "mobile_number": "+0987654321",
            "agreed_to_terms": False
        }
        
        try:
            response = requests.post(f"{self.api_url}/submissions", json=test_data)
            success = response.status_code == 400  # Should fail with 400
            details = f"Status: {response.status_code} (expected 400)"
            self.log_test("Create Submission Without Terms", success, details)
            return success
        except Exception as e:
            self.log_test("Create Submission Without Terms", False, str(e))
            return False

    def test_get_submissions(self):
        """Test getting all submissions"""
        try:
            response = requests.get(f"{self.api_url}/submissions")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = isinstance(data, list)
                details = f"Retrieved {len(data)} submissions"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Submissions", success, details)
            return success, response.json() if success else []
            
        except Exception as e:
            self.log_test("Get Submissions", False, str(e))
            return False, []

    def test_admin_verify_correct_password(self):
        """Test admin verification with correct password"""
        try:
            response = requests.post(f"{self.api_url}/admin/verify", json={"password": "admin123"})
            success = response.status_code == 200 and response.json().get("success") == True
            details = f"Status: {response.status_code}"
            self.log_test("Admin Verify (Correct Password)", success, details)
            return success
        except Exception as e:
            self.log_test("Admin Verify (Correct Password)", False, str(e))
            return False

    def test_admin_verify_wrong_password(self):
        """Test admin verification with wrong password (should fail)"""
        try:
            response = requests.post(f"{self.api_url}/admin/verify", json={"password": "wrongpassword"})
            success = response.status_code == 401  # Should fail with 401
            details = f"Status: {response.status_code} (expected 401)"
            self.log_test("Admin Verify (Wrong Password)", success, details)
            return success
        except Exception as e:
            self.log_test("Admin Verify (Wrong Password)", False, str(e))
            return False

    def test_delete_submission(self):
        """Test deleting a submission"""
        if not hasattr(self, 'test_submission_id'):
            self.log_test("Delete Submission", False, "No submission ID available for deletion")
            return False
            
        try:
            response = requests.delete(f"{self.api_url}/submissions/{self.test_submission_id}")
            success = response.status_code == 200 and response.json().get("success") == True
            details = f"Status: {response.status_code}"
            self.log_test("Delete Submission", success, details)
            return success
        except Exception as e:
            self.log_test("Delete Submission", False, str(e))
            return False

    def test_delete_nonexistent_submission(self):
        """Test deleting a non-existent submission (should fail)"""
        fake_id = "nonexistent-id-12345"
        try:
            response = requests.delete(f"{self.api_url}/submissions/{fake_id}")
            success = response.status_code == 404  # Should fail with 404
            details = f"Status: {response.status_code} (expected 404)"
            self.log_test("Delete Non-existent Submission", success, details)
            return success
        except Exception as e:
            self.log_test("Delete Non-existent Submission", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Client Intake API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 50)
        
        # Test API availability
        if not self.test_api_root():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        # Test submission creation
        success, submission_data = self.test_create_submission()
        
        # Test validation (terms required)
        self.test_create_submission_without_terms()
        
        # Test getting submissions
        self.test_get_submissions()
        
        # Test admin authentication
        self.test_admin_verify_correct_password()
        self.test_admin_verify_wrong_password()
        
        # Test deletion (if we have a submission to delete)
        if success:
            self.test_delete_submission()
        
        # Test deleting non-existent submission
        self.test_delete_nonexistent_submission()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return False

def main():
    tester = ClientIntakeAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": tester.tests_run,
            "passed_tests": tester.tests_passed,
            "success_rate": f"{(tester.tests_passed/tester.tests_run)*100:.1f}%",
            "results": tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())