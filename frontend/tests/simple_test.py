import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_backend_login_api(api_base_url):
    """Test the backend login API directly"""
    print(f"Testing backend login API at: {api_base_url}")

    # Test if login endpoint exists
    try:
        # Check what endpoints are available
        docs_response = requests.get(f"{api_base_url}/docs")
        print(f"✅ Backend docs accessible: {docs_response.status_code}")

        # Try to get OpenAPI spec to see available endpoints
        openapi_response = requests.get(f"{api_base_url}/openapi.json")
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            paths = openapi_data.get("paths", {})
            print(f"Available endpoints: {list(paths.keys())}")

        # Test login endpoint directly
        login_data = {"username": "test_user@test.com", "password": "test_password"}  # Using your test credentials

        # Try different login endpoint formats
        endpoints_to_try = ["/login/", "/login", "/auth/login", "/api/login"]

        for endpoint in endpoints_to_try:
            print(f"\nTrying login endpoint: {endpoint}")

            # Try form data (like your backend test)
            try:
                response = requests.post(f"{api_base_url}{endpoint}", data=login_data)
                print(f"  Form data response: {response.status_code}")
                if response.status_code != 404:
                    print(f"  Response content: {response.text[:200]}")
            except Exception as e:
                print(f"  Form data error: {e}")

            # Try JSON data
            try:
                response = requests.post(f"{api_base_url}{endpoint}", json=login_data)
                print(f"  JSON data response: {response.status_code}")
                if response.status_code != 404:
                    print(f"  Response content: {response.text[:200]}")
            except Exception as e:
                print(f"  JSON data error: {e}")

    except Exception as e:
        print(f"Error testing backend login: {e}")


def test_cors_preflight(api_base_url):
    """Test CORS preflight request"""
    print(f"Testing CORS from frontend to backend...")

    # Simulate preflight request
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }

    try:
        response = requests.options(f"{api_base_url}/login/", headers=headers)
        print(f"CORS preflight response: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"CORS error: {e}")


def test_frontend_network_debug(frontend_base_url):
    """Test frontend and inspect network errors"""
    print(f"Testing frontend login with network debugging...")

    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=0")
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("Navigating to frontend...")
        driver.get(f"{frontend_base_url}/login")

        wait = WebDriverWait(driver, 10)

        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        print("✅ Login form loaded")

        # Fill in login form
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")

        email_field.send_keys("test_user@test.com")
        password_field.send_keys("test_password")

        print("Credentials entered")

        # Enable browser console log capture
        logs_before = driver.get_log("browser")

        # Click login button
        login_button = driver.find_element(By.ID, "log-button")
        login_button.click()

        print("Login button clicked, waiting for response...")

        # Wait a bit for the request to complete
        time.sleep(3)

        # Check for errors in browser console
        logs_after = driver.get_log("browser")
        new_logs = logs_after[len(logs_before) :]

        print(f"Browser console logs ({len(new_logs)} new entries):")
        for log_entry in new_logs:
            print(f"  {log_entry['level']}: {log_entry['message']}")

        # Check current URL
        current_url = driver.current_url
        print(f"Current URL after login attempt: {current_url}")

        # Check for error messages on page
        try:
            error_element = driver.find_element(By.CLASS_NAME, "error-message")
            if error_element.is_displayed():
                print(f"Error message on page: {error_element.text}")
        except:
            print("No error message element found")

        # Check network tab if possible (this requires special setup)
        # For now, let's just check the page source for any obvious errors
        page_source = driver.page_source
        if "Failed to fetch" in page_source:
            print("❌ 'Failed to fetch' error found in page source")
        if "Network Error" in page_source:
            print("❌ 'Network Error' found in page source")

    finally:
        driver.quit()


def test_frontend_api_config(frontend_base_url):
    """Test that frontend is properly configured to use test backend"""
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait

    driver = webdriver.Chrome()
    try:
        # Go to frontend
        driver.get(frontend_base_url)
        wait = WebDriverWait(driver, 10)

        # Check if React environment variables are properly set
        # We can check this by looking at the console or network tab
        print("Checking frontend configuration...")

        # Execute JavaScript to check the API URL
        api_url = driver.execute_script(
            "return process?.env?.REACT_APP_API_URL || window.REACT_APP_API_URL || 'not found'"
        )
        print(f"Frontend API URL: {api_url}")

        # Try to make a test API call from the browser console
        test_script = """
            return fetch('/api/docs', {method: 'GET'})
                .then(response => response.status)
                .catch(error => error.message);
        """

        result = driver.execute_script(test_script)
        print(f"Frontend API test result: {result}")

    finally:
        driver.quit()
