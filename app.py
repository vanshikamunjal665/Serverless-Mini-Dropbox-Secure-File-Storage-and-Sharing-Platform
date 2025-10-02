import streamlit as st
import boto3
import requests
import pandas as pd
from warrant import Cognito
from botocore.exceptions import ClientError

# ------------------ CONFIGURATION ------------------
USER_POOL_ID = "ap-south-1_7cNCLfIHJ"  # your user pool ID
CLIENT_ID = "293fq4ihf3v1tt3fvhgjb3q0se"  # your app client ID
REGION = "ap-south-1"

# ------------------ SESSION STATE ------------------
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "cognito_user" not in st.session_state:
    st.session_state.cognito_user = None

# ------------------ STREAMLIT UI ------------------
st.title("File Upload Project")
option = st.radio("Choose an option:", ["Login", "Signup"])

# ------------------ SIGNUP ------------------
if option == "Signup":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    signup_button = st.button("Signup", key="signup_button")

    if signup_button and email and password:
        try:
            client = boto3.client("cognito-idp", region_name=REGION)

            response = client.sign_up(
                ClientId=CLIENT_ID,
                Username=email,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}]
            )

            st.success(f"✅ Signup successful for {email}. Verification code sent to email!")

        except Exception as e:
            st.error(f"Signup failed: {e}")

    # Verification input
    verification_code = st.text_input("Enter verification code sent to your email")
    verify_button = st.button("Verify Account", key="verify_button")
    if verify_button and email and verification_code:
        try:
            client = boto3.client("cognito-idp", region_name=REGION)
            client.confirm_sign_up(ClientId=CLIENT_ID, Username=email, ConfirmationCode=verification_code)
            st.success("✅ Account verified successfully!")
        except Exception as e:
            st.error(f"Verification failed: {e}")


# ------------------ LOGIN ------------------
if option == "Login":
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")
    login_button = st.button("Login", key="login_button")

    if login_button and email and password:
        try:
            client = boto3.client("cognito-idp", region_name=REGION)
            response = client.initiate_auth(
                ClientId=CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password
                }
            )
            st.session_state.is_logged_in = True
            st.session_state.username = email
            st.success(f"Logged in as {email}")
        except Exception as e:
            st.error(f"Login failed: {e}")


# ------------------ FILE UPLOAD ------------------
if st.session_state.is_logged_in:
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

    if uploaded_file:
        st.write(f"File selected: {uploaded_file.name}")

        if st.button("Upload", key="upload_button"):
            try:
                # Request presigned URL from backend
                presigned_response = requests.post(
                    "https://cxz6vkp8u2.execute-api.ap-south-1.amazonaws.com/prod/get-presigned-url",
                    json={"fileName": uploaded_file.name, "contentType": uploaded_file.type}
                ).json()

                upload_url = presigned_response["uploadURL"]
                file_id = presigned_response["fileId"]

                # Upload to S3
                upload_resp = requests.put(
                    upload_url,
                    data=uploaded_file.getvalue(),
                    headers={"Content-Type": uploaded_file.type}
                )

                if upload_resp.status_code == 200:
                    st.success("✅ File uploaded to S3 successfully!")

                    # Save metadata to DynamoDB
                    save_resp = requests.post(
                        "https://cxz6vkp8u2.execute-api.ap-south-1.amazonaws.com/prod/save-details",
                        json={"fileId": file_id, "fileName": uploaded_file.name}
                    ).json()

                    if save_resp.get("message") == "saved":
                        st.success("✅ File details saved to DynamoDB successfully!")
                    else:
                        st.error("❌ Failed to save file details.")
                else:
                    st.error(f"❌ File upload failed! Status code: {upload_resp.status_code}")

            except Exception as e:
                st.error(f"Error during upload: {e}")

    # ------------------ DISPLAY METADATA ------------------
    st.subheader("📂 Uploaded Files Metadata")
    try:
        dynamodb = boto3.client("dynamodb", region_name="ap-south-1")
        response = dynamodb.scan(TableName="DocumentMetadata")

        if "Items" in response and len(response["Items"]) > 0:
            data = []
            for item in response["Items"]:
                data.append({
                    "File ID": item.get("fileId", {}).get("S", ""),
                    "File Name": item.get("fileName", {}).get("S", ""),
                    "Type": item.get("contentType", {}).get("S", ""),
                    "Size": item.get("sizeHuman", {}).get("S", ""),
                    "Created At": item.get("createdAt", {}).get("S", "")
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No metadata found in DynamoDB.")

    except ClientError as e:
        st.error(f"Error fetching metadata: {e}")
