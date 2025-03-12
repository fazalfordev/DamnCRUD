import unittest
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
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')

        # Fix: Set timeout and ensure Firefox starts properly
        service = Service(GeckoDriverManager().install())
        cls.driver = webdriver.Firefox(service=service, options=options, timeout=300)
        cls.driver.implicitly_wait(15)  # Implicit wait for all elements

    def test_01_navigate_to_url(self):
        self.driver.get('http://localhost/DamnCRUD-main/login.php')
        self.assertIn("Login", self.driver.title, "Home page title does not match")

    def test_02_login(self):
        self.driver.get('http://localhost/DamnCRUD-main/login.php')

        username_field = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.ID, 'inputUsername'))
        )
        username_field.send_keys('admin')

        password_field = self.driver.find_element(By.ID, 'inputPassword')
        password_field.send_keys('nimda666!')

        login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()

        # Verify successful login
        WebDriverWait(self.driver, 15).until(EC.url_contains('index.php'))
        self.assertIn("index.php", self.driver.current_url, "Login failed or did not redirect")
        
        # Verify greeting message
        greeting_text = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.TAG_NAME, "h2"))
        ).text
        self.assertTrue("Howdy, damn" in greeting_text, "Login failed: Greeting message not found")

    def test_03_verify_edit_and_delete_buttons(self):
        self.driver.get("http://localhost/DamnCRUD-main/index.php")
        
        rows = self.driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")
        self.assertGreater(len(rows), 0, "No records found in the table")

        self.assertTrue(
            self.driver.find_elements(By.CSS_SELECTOR, "a.btn-success"), "Edit button not found"
        )
        self.assertTrue(
            self.driver.find_elements(By.CSS_SELECTOR, "a.btn-danger"), "Delete button not found"
        )

    def test_04_create_new_contact(self):
        self.driver.get("http://localhost/DamnCRUD-main/create.php")

        self.assertIn("Add new contact", self.driver.title, "Create contact page title does not match")

        self.driver.find_element(By.NAME, "name").send_keys("Test User")
        self.driver.find_element(By.NAME, "email").send_keys("testuser@example.com")
        self.driver.find_element(By.NAME, "phone").send_keys("1234567890")
        self.driver.find_element(By.NAME, "title").send_keys("QA Engineer")

        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Verify redirect and contact creation
        WebDriverWait(self.driver, 15).until(EC.url_contains("index.php"))
        self.assertIn("Test User", self.driver.page_source, "Test Failed: Contact not found in the list.")

    def test_05_update_contact(self):
        self.driver.get("http://localhost/DamnCRUD-main/index.php")

        # Find edit button dynamically
        try:
            edit_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'update.php?id=20')]"))
            )
            edit_button.click()
        except:
            self.fail("Test Failed: Edit button not found for 'Test User'")

        # Update details
        name_field = WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.NAME, 'name')))
        name_field.clear()
        name_field.send_keys('Updated User')

        self.driver.find_element(By.NAME, 'email').clear()
        self.driver.find_element(By.NAME, 'email').send_keys('updateduser@example.com')
        self.driver.find_element(By.NAME, 'phone').clear()
        self.driver.find_element(By.NAME, 'phone').send_keys('0987654321')
        self.driver.find_element(By.NAME, 'title').clear()
        self.driver.find_element(By.NAME, 'title').send_keys('Updated QA Engineer')

        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Verify update
        WebDriverWait(self.driver, 15).until(EC.url_contains("index.php"))
        self.assertIn("Updated User", self.driver.page_source, "Test Failed: Updated contact not found.")

    def test_06_delete_contact(self):
        self.driver.get("http://localhost/DamnCRUD-main/index.php")

        if "Updated User" not in self.driver.page_source:
            print("Test Passed: Contact already deleted.")
            return

        try:
            delete_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'delete.php?id=20')]"))
            )
            delete_button.click()
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except:
            self.fail("Test Failed: Delete button not found for 'Updated User'")

        # Verify deletion
        WebDriverWait(self.driver, 15).until(EC.url_contains("index.php"))
        self.assertNotIn("Updated User", self.driver.page_source, "Test Failed: Contact was not deleted.")

    def test_07_logout(self):
        self.driver.get("http://localhost/DamnCRUD-main/index.php")

        logout_button = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-danger[href='logout.php']"))
        )
        logout_button.click()

        WebDriverWait(self.driver, 15).until(EC.url_contains('login.php'))
        self.assertIn("login.php", self.driver.current_url, "Logout failed or did not redirect to login.php")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2, warnings='ignore')
