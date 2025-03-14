import os
import unittest
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service

class FormSubmissionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')  # Run in headless mode
        service = Service(GeckoDriverManager().install())
        cls.driver = webdriver.Firefox(service=service, options=options)
        cls.driver.implicitly_wait(10)
        # Use BASE_URL from environment or default to "http://localhost"
        cls.BASE_URL = os.getenv("BASE_URL", "http://localhost")
        print(f"🔍 Checking if server is running at: {cls.BASE_URL}/login.php")
        cls.wait_for_server()

    @classmethod
    def wait_for_server(cls):
        """Ensure the server is up before running tests."""
        for attempt in range(10):
            try:
                response = requests.get(cls.BASE_URL + "/login.php", timeout=5)
                print(f"✅ Attempt {attempt + 1}: Server responded with status {response.status_code}")
                if response.status_code == 200:
                    print("🎉 Server is up and running!")
                    return
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Attempt {attempt + 1}: Server not reachable ({e})")
            time.sleep(3)
        raise Exception("❌ Server is not responding. Check if it's running.")

    def ensure_logged_in(self):
        """
        If the current page is the login page or the title indicates login,
        perform login with known credentials.
        """
        if "login.php" in self.driver.current_url or "Login" in self.driver.title:
            self.driver.get(self.BASE_URL + "/login.php")
            username_field = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, 'inputUsername'))
            )
            username_field.clear()
            username_field.send_keys('admin')
            password_field = self.driver.find_element(By.ID, 'inputPassword')
            password_field.clear()
            password_field.send_keys('nimda666!')
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            # Wait until redirected to index page
            WebDriverWait(self.driver, 15).until(EC.url_contains('index.php'))

    def test_01_navigate_to_url(self):
        """Verify that the login page is reachable."""
        self.driver.get(self.BASE_URL + "/login.php")
        self.assertIn("Login", self.driver.title, "Login page title does not match")

    def test_02_login(self):
        """Test login functionality."""
        self.driver.get(self.BASE_URL + "/login.php")
        try:
            username_field = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, 'inputUsername'))
            )
            username_field.clear()
            username_field.send_keys('admin')
            password_field = self.driver.find_element(By.ID, 'inputPassword')
            password_field.clear()
            password_field.send_keys('nimda666!')
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            WebDriverWait(self.driver, 15).until(EC.url_contains('index.php'))
            self.assertIn("index.php", self.driver.current_url, "Login failed or did not redirect")
        except Exception as e:
            self.fail(f"Login test failed: {e}")

    def test_03_verify_edit_and_delete_buttons(self):
        """Check if edit and delete buttons exist in the employee table."""
        self.ensure_logged_in()
        self.driver.get(self.BASE_URL + "/index.php")
        rows = self.driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")
        self.assertGreater(len(rows), 0, "No records found in the table")
        self.assertTrue(self.driver.find_elements(By.CSS_SELECTOR, "a.btn-success"), "Edit button not found")
        self.assertTrue(self.driver.find_elements(By.CSS_SELECTOR, "a.btn-danger"), "Delete button not found")

    def test_04_create_new_contact(self):
        """Create a new contact and verify it appears in the table."""
        self.ensure_logged_in()
        self.driver.get(self.BASE_URL + "/create.php")
        # Verify that the page title contains the expected text.
        self.assertIn("Add new contact", self.driver.title, "Create contact page title does not match")
        self.driver.find_element(By.NAME, "name").send_keys("Test User")
        self.driver.find_element(By.NAME, "email").send_keys("testuser@example.com")
        self.driver.find_element(By.NAME, "phone").send_keys("1234567890")
        self.driver.find_element(By.NAME, "title").send_keys("QA Engineer")
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(self.driver, 15).until(EC.url_contains("index.php"))
        self.assertIn("Test User", self.driver.page_source, "Contact not found after creation.")

    def test_05_update_contact(self):
        """Update the existing contact details."""
        self.ensure_logged_in()
        self.driver.get(self.BASE_URL + "/index.php")
        try:
            # Locate the first update button using a generic XPath.
            edit_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'update.php?id=')]"))
            )
            edit_button.click()
        except Exception as e:
            self.fail("Edit button not found. Exception: " + str(e))
        name_field = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.NAME, 'name'))
        )
        name_field.clear()
        name_field.send_keys('Updated User')
        email_field = self.driver.find_element(By.NAME, 'email')
        email_field.clear()
        email_field.send_keys('updateduser@example.com')
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(self.driver, 15).until(EC.url_contains("index.php"))
        self.assertIn("Updated User", self.driver.page_source, "Updated contact not found.")

    def test_06_delete_contact(self):
        """Delete the contact and verify it is removed."""
        self.ensure_logged_in()
        self.driver.get(self.BASE_URL + "/index.php")
        if "Updated User" not in self.driver.page_source:
            print("Test Passed: Contact already deleted.")
            return
        try:
            delete_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'delete.php?id=')]"))
            )
            delete_button.click()
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except Exception as e:
            self.fail("Delete button not found. Exception: " + str(e))
        WebDriverWait(self.driver, 15).until(EC.url_contains("index.php"))
        self.assertNotIn("Updated User", self.driver.page_source, "Contact was not deleted.")

    def test_07_logout(self):
        """Logout and verify redirection to login page."""
        self.ensure_logged_in()
        self.driver.get(self.BASE_URL + "/index.php")
        try:
            logout_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-danger[href='logout.php']"))
            )
            logout_button.click()
            WebDriverWait(self.driver, 15).until(EC.url_contains('login.php'))
            self.assertIn("login.php", self.driver.current_url, "Logout failed.")
        except Exception as e:
            self.fail("Logout button not found. Exception: " + str(e))

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)
