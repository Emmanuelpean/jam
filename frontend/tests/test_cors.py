# After backend and frontend start, test CORS from browser
print("\n" + "=" * 80)
print("TESTING CORS FROM BROWSER".center(80))
print("=" * 80)
import time

# Create a temporary driver to test CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def test_cors(frontend_base_url):
    """Test CORS configuration from browser perspective"""

    test_options = Options()
    test_options.add_argument("--headless=new")
    test_options.add_argument("--window-size=1920,1080")

    test_driver = webdriver.Chrome(options=test_options)

    try:
        # Navigate to frontend
        print(f"\nNavigating to: {frontend_base_url}/login")
        test_driver.get(f"{frontend_base_url}/login")
        time.sleep(2)

        # Execute a fetch request from browser console
        print("\nTesting CORS from browser...")

        result = test_driver.execute_async_script(
            """
            const callback = arguments[arguments.length - 1];

            fetch('http://localhost:8000/health', {
                method: 'GET',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => {
                callback({
                    status: response.status,
                    ok: response.ok,
                    corsError: false
                });
            })
            .catch(error => {
                callback({
                    status: 0,
                    ok: false,
                    corsError: true,
                    error: error.toString()
                });
            });
        """
        )

        print(f"\n{'='*60}")
        print(f"CORS TEST RESULT")
        print(f"{'='*60}")
        print(f"Status:      {result['status']}")
        print(f"Success:     {result['ok']}")
        print(f"CORS Error:  {result['corsError']}")

        if result["corsError"]:
            print(f"Error:       {result.get('error', 'Unknown')}")
            print(f"{'='*60}")
            print("❌ CORS is blocking browser requests!")
            print("This confirms the CORS configuration is not working.")
        else:
            print(f"{'='*60}")
            print("✅ CORS is working correctly from browser!")

        # Also test the actual login endpoint
        print(f"\nTesting CORS on /login endpoint...")

        login_result = test_driver.execute_async_script(
            """
            const callback = arguments[arguments.length - 1];

            const formData = new URLSearchParams();
            formData.append('username', 'test_user@test.com');
            formData.append('password', 'test_password');

            fetch('http://localhost:8000/login/', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: formData
            })
            .then(response => {
                callback({
                    status: response.status,
                    ok: response.ok,
                    corsError: false
                });
            })
            .catch(error => {
                callback({
                    status: 0,
                    ok: false,
                    corsError: true,
                    error: error.toString()
                });
            });
        """
        )

        print(f"\n{'='*60}")
        print(f"LOGIN ENDPOINT CORS TEST")
        print(f"{'='*60}")
        print(f"Status:      {login_result['status']}")
        print(f"Success:     {login_result['ok']}")
        print(f"CORS Error:  {login_result['corsError']}")
        assert login_result["status"] == 200

        if login_result["corsError"]:
            print(f"Error:       {login_result.get('error', 'Unknown')}")
            print(f"{'='*60}")
            print("❌ CORS is blocking login requests!")

            # Get browser console logs
            logs = test_driver.get_log("browser")
            if logs:
                print("\nBrowser Console Errors:")
                for log in logs:
                    if "SEVERE" in log["level"]:
                        print(f"  🔴 {log['message']}")
        else:
            print(f"{'='*60}")
            print("✅ CORS is working on login endpoint!")
            print(f"Note: Status {login_result['status']} might be 403/422 (invalid creds) but no CORS error")

        # Assert that CORS is working
        assert not result["corsError"], f"CORS is blocking requests: {result.get('error', 'Unknown')}"

    finally:
        test_driver.quit()
