def test_simple_login(frontend_base_url, api_base_url):
    """Simple standalone test for login functionality"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    import time

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(options=options)

    try:

        # Navigate to login page
        print("\n1. Navigating to login page...")
        driver.get("http://localhost:3000/jam/login")
        time.sleep(2)

        # Fill in credentials
        print("2. Filling in credentials...")
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")

        email_field.send_keys("test_user@test.com")
        password_field.send_keys("test_password")

        # Test with direct fetch first
        print("3. Testing login with direct fetch...")
        result = driver.execute_async_script(
            """
            const callback = arguments[arguments.length - 1];

            const formData = new URLSearchParams();
            formData.append('username', 'test_user@test.com');
            formData.append('password', 'test_password');

            fetch('http://localhost:8000/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData
            })
            .then(async response => {
                const text = await response.text();
                callback({
                    status: response.status,
                    statusText: response.statusText,
                    body: text
                });
            })
            .catch(error => {
                callback({
                    status: 0,
                    error: error.toString(),
                    errorMessage: error.message
                });
            });
        """
        )

        print(f"\n{'='*60}")
        print(f"FETCH RESULT:")
        print(f"  Status: {result['status']}")
        print(f"  Response: {result.get('body', result.get('error', 'N/A'))}")
        print(f"{'='*60}\n")

        # Get console logs
        logs = driver.get_log("browser")
        if logs:
            print("Browser Console:")
            for log in logs:
                print(f"  [{log['level']}] {log['message']}")

        # Assert
        if result["status"] == 0:
            print(f"\n❌ FAILED: Request blocked (status 0)")
            print(f"   Error: {result.get('error', 'Unknown')}")
        elif result["status"] == 200:
            print(f"\n✅ SUCCESS: Login worked!")
        else:
            print(f"\n⚠️  Request completed with status {result['status']}")

        assert result["status"] != 0, f"Request blocked: {result.get('error')}"

    finally:
        driver.quit()
