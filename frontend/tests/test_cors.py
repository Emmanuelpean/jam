# After backend and frontend start, test CORS from browser
print("\n" + "=" * 80)
print("TESTING CORS FROM BROWSER".center(80))
print("=" * 80)
import time

# Create a temporary driver to test CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def test_cors(frontend_url):
    test_options = Options()
    test_options.add_argument("--headless=new")

    test_driver = webdriver.Chrome(options=test_options)

    try:
        # Navigate to frontend
        test_driver.get(f"{frontend_url}/login")
        time.sleep(2)

        # Execute a fetch request from browser console
        cors_test_script = """
        return fetch('http://localhost:8000/health', {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        })
        .then(response => ({
            status: response.status,
            ok: response.ok,
            corsError: false
        }))
        .catch(error => ({
            status: 0,
            ok: false,
            corsError: true,
            error: error.toString()
        }));
        """

        result = test_driver.execute_async_script(
            """
            const callback = arguments[arguments.length - 1];
            """
            + cors_test_script.replace("return ", "")
            + """
            .then(callback);
        """
        )

        print(f"Browser CORS Test Result:")
        print(f"  Status: {result['status']}")
        print(f"  Success: {result['ok']}")
        print(f"  CORS Error: {result['corsError']}")

        if result["corsError"]:
            print("  ❌ CORS is blocking browser requests!")
            print(f"  Error: {result.get('error', 'Unknown')}")
        else:
            print("  ✅ CORS is working correctly!")

    finally:
        test_driver.quit()

    print("=" * 80 + "\n")
