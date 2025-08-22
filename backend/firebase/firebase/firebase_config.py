import firebase_admin
from firebase_admin import credentials, auth
import os

# Path to the service account key
cred = credentials.Certificate("firebase/serviceAccountKey.json")

# Initialize Firebase app only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
