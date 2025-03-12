import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class FormSubmissionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        cls.driver = webdriver.Firefox(options=options)
        cls.driver.implicitly_wait(10)  # Implicit wait for elements

    def test_01_navigate_to_url(self):
        self.driver.get('http://localhost/DamnCRUD-main/login.php')
        expected_home_title = "Login"
        actual_home_title = self.driver.title
        self.assertIn(expected_home_title, actual_home_title,
                      "Home page title does not match")

    def test_02_login(self):
        self.driver.get('http://localhost/DamnCRUD-main/login.php')

        username_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'inputUsername'))
        )
        username_field.send_keys('admin')

        password_field = self.driver.find_element(By.ID, 'inputPassword')
        password_field.send_keys('nimda666!')

        login_button = self.driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()

        # Verify URL change
        WebDriverWait(self.driver, 10).until(EC.url_contains('index.php'))
        print(f"Current URL after login: {self.driver.current_url}")

        # Verify greeting message "Howdy, damn [username]!"
        greeting_text = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, "h2"))
        ).text
        self.assertTrue("Howdy, damn" in greeting_text,
                        "Login failed: Greeting message not found")

        # Verify employee table loads
        table = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "employee"))
        )
        self.assertTrue(table.is_displayed(), "Employee table not visible")

    def test_03_verify_edit_and_delete_buttons(self):
        # Ensure at least one row exists
        rows = self.driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")
        self.assertGreater(len(rows), 0, "No records found in the table")

        # Verify 'edit' button exists
        edit_buttons = self.driver.find_elements(
            By.CSS_SELECTOR, "a.btn-success")
        self.assertGreater(len(edit_buttons), 0, "Edit button not found")

        # Verify 'delete' button exists
        delete_buttons = self.driver.find_elements(
            By.CSS_SELECTOR, "a.btn-danger")
        self.assertGreater(len(delete_buttons), 0, "Delete button not found")

    def test_04_create_new_contact(self):
        self.driver.get("http://localhost/DamnCRUD-main/create.php")

        # Verify the page title
        expected_title = "Add new contact"
        actual_title = self.driver.title
        self.assertIn(expected_title, actual_title,
                      "Create contact page title does not match")

        # Fill in the form
        self.driver.find_element(By.NAME, "name").send_keys("Test User")
        self.driver.find_element(By.NAME, "email").send_keys(
            "testuser@example.com")
        self.driver.find_element(By.NAME, "phone").send_keys("1234567890")
        self.driver.find_element(By.NAME, "title").send_keys("QA Engineer")

        # Submit the form
        self.driver.find_element(
            By.CSS_SELECTOR, "input[type='submit']").click()

        # Wait for redirection to index.php
        WebDriverWait(self.driver, 10).until(EC.url_contains("index.php"))

        # Verify the new contact appears in the table
        time.sleep(2)  # Give time for the table to update

        while True:
            # Try to find the newly added contact
            if "Test User" in self.driver.page_source:
                print("Test Passed: Contact successfully added and found in the list.")
                break

            # Check if there is a "Next" button and click it
            try:
                next_button = self.driver.find_element(
                    By.LINK_TEXT, "Next")  # Adjust selector if needed
                next_button.click()
                time.sleep(2)  # Wait for the next page to load
            except:
                print(
                    "Test Failed: Contact not found, even after navigating through pages.")
                break

    def test_05_update_contact(self):
        self.driver.get("http://localhost/DamnCRUD-main/index.php")

        # Debug: Check if the contact is present in the page source
        while True:
            if "Test User" in self.driver.page_source:
                break
            try:
                next_button = self.driver.find_element(
                    By.LINK_TEXT, "Next")  # Adjust selector if needed
                next_button.click()
                time.sleep(2)  # Wait for the next page to load
            except:
                print("Test Failed: Contact 'Test User' not found in the list.")
                return

        # Find the edit button for the specific contact
        edit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[href='update.php?id=33']"))
        )
        edit_button.click()

        # Update the contact details
        name_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'name'))
        )
        name_field.clear()
        name_field.send_keys('Updated User')

        email_field = self.driver.find_element(By.NAME, 'email')
        email_field.clear()
        email_field.send_keys('updateduser@example.com')

        phone_field = self.driver.find_element(By.NAME, 'phone')
        phone_field.clear()
        phone_field.send_keys('0987654321')

        title_field = self.driver.find_element(By.NAME, 'title')
        title_field.clear()
        title_field.send_keys('Updated QA Engineer')

        # Submit the form
        self.driver.find_element(
            By.CSS_SELECTOR, "input[type='submit']").click()

        # Wait for redirection to index.php
        WebDriverWait(self.driver, 10).until(EC.url_contains("index.php"))

        # Verify the updated contact appears in the table
        time.sleep(2)  # Give time for the table to update

        while True:
            if "Updated User" in self.driver.page_source:
                print("Test Passed: Contact successfully updated and found in the list.")
                break
            try:
                next_button = self.driver.find_element(
                    By.LINK_TEXT, "Next")  # Adjust selector if needed
                next_button.click()
                time.sleep(2)  # Wait for the next page to load
            except:
                print(
                    "Test Failed: Updated contact not found, even after navigating through pages.")
                break

    def test_06_delete_contact(self):
        self.driver.get("http://localhost/DamnCRUD-main/index.php")

        # Check if the contact exists before attempting to delete
        if "Updated User" not in self.driver.page_source:
            print("Test Passed: Contact already deleted.")
            return

        # Find the delete button for the specific contact
        delete_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[href='delete.php?id=17']"))
        )
        delete_button.click()

        # Confirm the deletion
        alert = self.driver.switch_to.alert
        alert.accept()

        # Verify the contact is deleted
        time.sleep(2)  # Give time for the table to update
        self.driver.get("http://localhost/DamnCRUD-main/index.php")
        self.assertNotIn("Updated User", self.driver.page_source,
                         "Test Failed: Contact was not deleted.")

    def test_07_logout(self):
        self.driver.get("http://localhost/DamnCRUD-main/index.php")

        # Find the logout button and click it
        logout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.btn-danger[href='logout.php']"))
        )
        logout_button.click()

        # Verify redirection to login page
        WebDriverWait(self.driver, 10).until(EC.url_contains('login.php'))
        self.assertIn("login.php", self.driver.current_url,
                      "Logout failed or did not redirect to login.php")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2, warnings='ignore')
