import pyrebase

# ----------------------------
# FIREBASE CONFIG
# ----------------------------
firebaseConfig = {
    "apiKey": "AIzaSyDacuASufZPnvtq_wvBpThW1xosE3ZUobs",
    "authDomain": "trading-bot-app-2162f.firebaseapp.com",
    "databaseURL": "https://trading-bot-app-2162f-default-rtdb.firebaseio.com/",
    "projectId": "trading-bot-app-2162f",
    "storageBucket": "trading-bot-app-2162f.firebasestorage.app",
    "messagingSenderId": "230500475531",
    "appId": "1:230500475531:web:d740bbd80d89bf60e5aa8e"
}

firebase = pyrebase.initialize_app(firebaseConfig)
S
auth = firebase.auth()
db = firebase.database()  # 🔥 NEW

# ----------------------------
# SIGNUP
# ----------------------------
def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)

        # Save basic user data in database
        user_id = user['localId']
        db.child("users").child(user_id).set({
            "email": email,
            "created_at": "now"
        })

        return user
    except Exception as e:
        print("Signup error:", e)
        return None

# ----------------------------
# LOGIN
# ----------------------------
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        print("Login error:", e)
        return None