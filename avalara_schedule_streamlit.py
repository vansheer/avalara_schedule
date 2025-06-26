import streamlit as st
import requests
import pandas as pd

# Set display options
pd.set_option('display.max_colwidth', None)

# Set page layout to wide
st.set_page_config(page_title="Avalara Import Schedule Viewer", layout="wide")

# Helper function
def extract_non_empty_duties(node, result=None):
    if result is None:
        result = []

    if isinstance(node, dict):
        duties = node.get("duties")
        if isinstance(duties, dict) and duties:
            result.append(duties)

        children = node.get("children", [])
        for child in children:
            extract_non_empty_duties(child, result)

    return result

# Streamlit UI
st.title("Avalara Import Schedule Viewer")

hs_code = st.text_input("Enter HS Code (e.g., 7323.93.0080):")
country_of_origin = st.text_input("Enter Country of Origin (ISO 2-char code):", "CN")
country_of_destination = st.text_input("Enter Country of Destination (ISO 2-char code):", "US")

if st.button("Get Import Schedule"):
    # Prepare inputs
    hs_code_cleaned = hs_code.replace('.', '')
    API_URL = f"https://info.stage.3ceonline.com/ccce/apis/tradedata/import/v1/schedule/{hs_code_cleaned}/{country_of_origin}/{country_of_destination}"

    TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiJoaXQgcHJvbW90aW9uYWwgYXBpIHVzZXIiLCJzeXN0ZW1faWQiOiIwZmQzMjZmOC0xOGFiLTQ5ZTUtOTRiZS05MjE4YWMzYWY4M2UiLCJwcm9maWxlX2lkIjoiZmE0NTFjZDQxYTRhNDc1ZmJhM2U5ZGY2ZGZhNGQ4YWEiLCJzY29wZSI6WyJTVEFHRSJdLCJleHAiOjE3NTIwNjgyNjgsImF1dGhvcml0aWVzIjpbIlJPTEVfQ0VSVElGSUNBVEUiLCJST0xFX05PVEVTIiwiUk9MRV9UQVJJRkZfRUxJR0lCSUxJVFkiLCJST0xFX0NMQVNTSUZJQ0FUSU9OIiwiUk9MRV9UUkFERURBVEEiLCJST0xFX1VTRVIiXSwianRpIjoiMWNjMDZkMWQtMjk4ZC00NGE4LWFmODYtZTIyMDEwZTQzOGMwIiwiY2xpZW50X2lkIjoiSGl0UHJvbW90aW9uYWxQcm9kdWN0c19hcGlfY2xpZW50In0.AZ1hvRC1DsfU48KzdSc3Kp3GQTquNcoP-WwyVIW6EDqwxXPlqYErD_-ZqgVvs4Thr0GXZPtteV6ktdaajP37Au31AO6HnyQpko88_IFG1tOw-Wbz_UuZRtCuQbbLZLBYIHEx572DJvqBSscuACeQnPKxKE--tqwBeP0jJG35aFGJK2TbAaB5emdKgT4m-WpiJbVRbLTfSFE84d7w4mDlMJ4xKvliyMKWmzfMYyGi3fdnLWUbM9s8fPat29JEMFCNfvnT68tg_xTBpc6WzWx6A09KiOg9rdSfVkzYiDOhwtNJK3-7QsBcBW5p1ILlzlK4OP-DwTO1NwoZDq_bZ3omYg"  # Replace with your actual token
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        duties = extract_non_empty_duties(data)

        if duties:
            duty_data = []
            for key in duties[0]:
                duty = duties[0][key]
                duty_data.append(duty)

            df = pd.DataFrame(duty_data)
            df.rename(
                columns={
                    'name': 'Duty',
                    'longName': 'Full Description',
                    'rate': 'Duty Rate'
                },
                inplace=True
            )
            st.success("Duties extracted successfully.")
            st.dataframe(df[['Duty', 'Full Description', 'Duty Rate']])
        else:
            st.warning("No duties found in response.")
    else:
        st.error(f"API Error {response.status_code}: {response.text}")
