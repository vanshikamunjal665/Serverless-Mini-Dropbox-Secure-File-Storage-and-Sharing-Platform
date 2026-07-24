# 📦 Mini Dropbox - Serverless File Storage & Sharing Platform

A Dropbox-like cloud file storage and sharing web app built entirely on **serverless AWS infrastructure**, with a **Streamlit** frontend. Users can register/login, upload files directly to S3 via pre-signed URLs, view their files, download them, delete them, and generate temporary shareable links - with zero servers to manage on the backend, and zero hosting cost for the frontend.

**🔗 Live App:** `https://serverless-mini-dropbox-file-storage-and-sharing-platform.streamlit.app/`

---

## 🖼️ Preview

| Login | Dashboard |
|---|---|
| ![Login Page](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) |

> Replace the images above (and throughout this README) by adding your own screenshots to a `screenshots/` folder in the repo root. Full list in the [Screenshots](#-screenshots) section.

---

## 🚀 Features

- 🔐 **Authentication** — Sign up, email verification, and login via Amazon Cognito (JWT-based)
- 📤 **Upload** — Direct-to-S3 upload using pre-signed URLs (files never pass through a server)
- 📄 **List Files** — Per-user file listing pulled from DynamoDB
- ⬇️ **Download** — Secure, time-limited pre-signed download links
- 🔗 **Share** — Generate temporary shareable links with configurable expiry
- 🗑️ **Delete** — Removes both the S3 object and its DynamoDB metadata
- 📊 **Dashboard metrics** — Total files, real storage used, and files shared this session
- ⏳ **Post-upload sync** — Frontend polls briefly after upload so newly uploaded files appear without needing a manual refresh/logout
- 🧩 **Fully serverless backend** — No EC2, no containers, pay only per request
- ☁️ **Zero-cost, always-on frontend hosting** via Streamlit Community Cloud

---

## 🏗️ Architecture

```
┌─────────────┐        HTTPS         ┌──────────────────┐
│  Streamlit  │ ───────────────────► │  Amazon Cognito  │  (Sign up / Login)
│  Frontend   │ ◄─────────────────── │  (User Pool)     │
│ (Streamlit  │      JWT Tokens      └──────────────────┘
│  Cloud)     │
└──────┬──────┘
       │
       │  Bearer <AccessToken>
       ▼
┌─────────────────────┐
│ Amazon API Gateway  │  (HTTP API, Cognito JWT Authorizer)
│  /upload  /files    │
│  /download /file    │
│  /share             │
└──────────┬──────────┘
           │ invokes
           ▼
┌────────────────────────┐        ┌───────────────────┐
│   AWS Lambda           │ ─────► │  Amazon DynamoDB  │  (File metadata)
│  (5 request functions) │        └───────────────────┘
│                        │ ─────► ┌───────────────────┐
└────────┬───────────────┘        │   Amazon S3       │  (File storage)
         │                        └────────┬──────────┘
         │ triggered on ObjectCreated      │
         ▼                                 │
┌────────────────────────┐                 │
│ store-file-metadata    │ ◄───────────────┘
│  Lambda (S3 trigger)   │
│  writes metadata to    │
│  DynamoDB including    │
│  file size             │
└────────────────────────┘
```

**Flow summary:**
1. User signs up / logs in via Cognito → receives a JWT Access Token.
2. Frontend calls API Gateway endpoints with `Authorization: Bearer <token>`.
3. API Gateway validates the JWT (Cognito JWT Authorizer) before invoking Lambda.
4. Upload: Lambda returns a pre-signed S3 PUT URL → frontend uploads the file **directly to S3**.
5. An S3 `ObjectCreated` event asynchronously triggers a separate Lambda that writes file metadata (name, size, owner, timestamp) into DynamoDB.
6. The frontend briefly polls `/files` right after upload so the new file appears as soon as that async write completes, instead of requiring a manual refresh.
7. All other operations (list/download/delete/share) read/write DynamoDB and generate pre-signed S3 URLs as needed.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Python, Streamlit |
| Frontend Hosting | Streamlit Community Cloud (free, always-on) |
| Authentication | Amazon Cognito (User Pool + App Client) |
| API Layer | Amazon API Gateway (HTTP API) with JWT Authorizer |
| Compute | AWS Lambda (Python 3.x) |
| Storage | Amazon S3 (pre-signed URLs, no public access) |
| Database | Amazon DynamoDB (on-demand capacity) |
| IAM | Least-privilege execution roles per Lambda + scoped deploy user |

---

## ☁️ AWS Services Used

- **Amazon Cognito** — User Pool for authentication; issues JWT Access/ID/Refresh tokens.
- **AWS Lambda** — Six functions total:
  - `generate-upload-url` — creates a pre-signed S3 PUT URL
  - `list-files` — queries DynamoDB for the logged-in user's files
  - `download-file` — creates a pre-signed S3 GET URL
  - `delete-file` — deletes the S3 object + DynamoDB record
  - `share-file` — creates a time-limited pre-signed share URL
  - `store-file-metadata` — S3 event-triggered function that writes metadata (including file size) after upload
- **Amazon API Gateway (HTTP API)** — Routes requests to Lambda, secured with a Cognito JWT Authorizer.
- **Amazon S3** — Stores raw file objects under `uploads/<user_id>/<uuid>_<filename>`; CORS configured to allow `PUT`/`GET` from the deployed frontend origin.
- **Amazon DynamoDB** — Table keyed on `UserID` (partition key) + `FileID` (sort key), storing file metadata including `FileSize`.
- **IAM** — Scoped Lambda execution roles, plus a dedicated deploy-time IAM user restricted to `cognito-idp:InitiateAuth`, `SignUp`, `ConfirmSignUp` only.

**CloudFront was deliberately not used** — API Gateway and S3 pre-signed URLs already serve over HTTPS, and Streamlit Cloud provides HTTPS for the frontend. CloudFront would add cost and complexity (custom domain, CDN caching, WAF) with no benefit at this project's scale.

---

## 📁 Project Structure

### Backend (AWS Lambda functions)
```
backend/
└── lambdas/
    ├── generate-upload-url/
    │   └── lambda_function.py
    ├── list-files/
    │   └── lambda_function.py       # JSON-serializes DynamoDB Decimal types
    ├── download-file/
    │   └── lambda_function.py
    ├── delete-file/
    │   └── lambda_function.py
    ├── share-file/
    │   └── lambda_function.py
    └── store-file-metadata/
        └── lambda_function.py       # captures FileSize from the S3 event
```

### Frontend (Streamlit)
```
frontend/
├── app.py                     # Entry point — controls navigation only
├── core/
│   ├── __init__.py
│   ├── config.py                # AWS/API constants
│   ├── session.py                 # Session-state helpers (login state, tokens)
│   └── formatters.py                # Display formatting (e.g. byte sizes)
├── services/
│   ├── __init__.py
│   ├── cognito_service.py             # Login / sign up / confirm (Cognito, secrets-aware)
│   └── storage_service.py               # Upload / list / download / delete / share (API Gateway)
├── views/
│   ├── __init__.py
│   ├── login_view.py                     # Login / Sign Up / Confirm UI
│   └── dashboard_view.py                   # Metrics, upload (with post-upload sync), file list, actions
├── assets/
│   └── style.css
└── requirements.txt
```

---

## 🔌 API Reference

All endpoints require:
```
Authorization: Bearer <Cognito Access Token>
```

| Method | Endpoint | Request Body / Params | Response |
|---|---|---|---|
| `POST` | `/upload` | `{ "filename": "report.pdf" }` | `{ "uploadURL": "...", "fileKey": "..." }` — client then `PUT`s file bytes to `uploadURL` |
| `GET` | `/files` | – | `[ { "FileID", "FileName", "FileKey", "UploadTime", "FileSize", "Bucket", "UserID" } ]` |
| `GET` | `/download` | Query param: `fileId` | `{ "downloadURL": "..." }` |
| `DELETE` | `/file` | `{ "fileId": "..." }` | `{ "message": "File deleted successfully" }` |
| `POST` | `/share` | `{ "fileId": "...", "expiresIn": 3600 }` | `{ "shareURL": "...", "expiresIn": 3600 }` |

---

## 💰 Notes on Cost & Hosting

The AWS backend is **fully serverless** — Lambda, API Gateway, DynamoDB (on-demand), S3, and Cognito all bill per request/use, not for idling. There is nothing to "turn off," and no cost accrues while the app isn't being used beyond negligible S3 storage.

The Streamlit frontend is a long-running process and needs somewhere to stay alive continuously — hosting it on **Streamlit Community Cloud** keeps the whole project reachable 24/7 at zero cost, without needing to keep any personal machine or EC2 instance running.

**CloudFront was not added** since API Gateway, S3 pre-signed URLs, and Streamlit Cloud already serve everything over HTTPS by default — a CDN would add cost and complexity without meaningful benefit at this project's traffic scale.

---

## 🐛 Known Issues Resolved During Development

| Issue | Root Cause | Fix |
|---|---|---|
| `Object of type Decimal is not JSON serializable` after adding file size | `boto3` returns DynamoDB numeric fields as `Decimal`, which `json.dumps` can't serialize by default | Added a custom `DecimalEncoder` in `list-files` Lambda |
| Storage Used always showed "N/A" | `FileSize` was never captured or stored | `store-file-metadata` now reads `record["s3"]["object"]["size"]` from the S3 event and stores it |
| Newly uploaded file didn't appear until logout/login | The S3 → Lambda metadata write is asynchronous, so an immediate refresh raced ahead of it | Frontend now briefly polls `/files` after upload until the new file appears, instead of refreshing instantly |
| Streamlit auto-generated an unwanted sidebar | Streamlit auto-detects any folder literally named `pages/` as multipage navigation | Renamed the views folder to `views/` to avoid the auto-detection entirely |

---

## 📸 Screenshots

Create a `screenshots/` folder in the repo root and add the following (referenced throughout this README):

| File name | What to capture |
|---|---|
| `login.png` | Login page |
| `signup.png` | Sign up tab |
| `confirm.png` | Confirm account tab |
| `dashboard.png` | Full dashboard after login |
| `upload.png` | Upload in progress / success message |
| `file-list.png` | "My Files" section with uploaded files |
| `download.png` | Download link generated |
| `share.png` | Share link generated |
| `cognito-pool.png` | Cognito User Pool console |
| `dynamodb-table.png` | DynamoDB table items (showing `FileSize` populated) |
| `lambda-functions.png` | List of deployed Lambda functions |
| `api-gateway-routes.png` | API Gateway routes configuration |
| `deployed-app.png` | Live deployed Streamlit app |

---

## 🔮 Future Improvements

- File size backfill script for files uploaded before size tracking was added
- Synchronous metadata write on upload (dedicated endpoint) to remove the polling delay entirely
- Folder/nested-path support
- File preview (images/PDFs) before download
- Storage quota per user
- Multi-file (batch) upload
- Activity log / audit trail per file

---

## 👤 Author

**Your Name**
Built as a personal/academic project to demonstrate a fully serverless AWS architecture with a Python frontend.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
