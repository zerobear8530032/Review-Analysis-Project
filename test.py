import requests

def check_api_response(api_url, api_key, params=None):
    # Define the parameters for the API call
    params = params or {}
    params['api_key'] = api_key  # Add the api_key parameter to the request

    try:
        # Send GET request to the API
        response = requests.get(api_url, params=params)

        # Check if the response status code is 200 (success)
        if response.status_code == 200:
            print("Success!")
            print("Response data:", response.json())  # Print the response content as a JSON object
        else:
            print(f"Error: {response.status_code}")
            print("Response data:", response.json())  # Print the error response content

    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    # Example API endpoint
    api_url = "http://localhost:5000/api/product_data"  # Replace with your API endpoint URL

    # Example API key
    api_key = "d62ffb9f60cd7104b885c5248e8bb17a"  # Replace with your valid API key

    # Example URL parameter to test with
    test_url = "https://www.amazon.in/Apple-iPhone-13-128GB-Midnight/dp/B09G9HD6PD/ref=sr_1_1_sspa?crid=2WW2L3P6UU9C5&dib=eyJ2IjoiMSJ9.OCoJgZ8ghdguKvc7Ozmt3OyY3JIh2zh_9fXQPStOsFy5Gz9e2PbRJTLGIEpMmwnd9CVu_0AItnBKvK-Pq77gJAGlvlx3e9LCxkoBYj-AnFwucWk8rO7vzCPYEx0vtRSqrp-9ZHIPhzwQjMDYvJLDxKU3_eYofWryI6oyDNBR9NqdE24JD7kQ6Pom11Z9GUFOdVoNvj_44EhFuz_Pv67eDtfnOdkbrxLtb-21_mpIJFE.Uv5YExEzvX3OP1UdOYyL5Tb8bXComK-ahT2aVAxlX4w&dib_tag=se&keywords=iphone&qid=1728323512&sprefix=ipho%2Caps%2C274&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1"  # Replace with a valid URL for testing
    # test_url="https://www.flipkart.com/xiaomi-14-civi-matcha-green-512-gb/p/itm6683aeab2b5bd?pid=MOBHFGU7HKHZCJGE&lid=LSTMOBHFGU7HKHZCJGERFB280&marketplace=FLIPKART&store=tyy%2F4io&srno=b_1_1&otracker=nmenu_sub_Electronics_0_Mi&fm=search-autosuggest&iid=en_XzAy_EOnU1FuBSp_8g-PPVu2IVIU0c1iInrkE82m_pGIPSVZBoMuzD451rYMq5BUmf1RkWCJd0Ix1ecjWzA3ifUFjCTyOHoHZs-Z5_PS_w0%3D&ppt=pp&ppn=pp&ssid=7m821at0dc0000001730143255537"
    # Check API response for the /api/scrapper endpoint
    check_api_response(api_url, api_key, params={"url": test_url})
