import pickle
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth

names = ["Peter pParker", "Rebecca Miller"]
usernames = ["pparker", "rmiler"]
passwords = ["abc1233", "def456"]

hashed_passwords = stauth.hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file :
    pickle.dump(hashed_passwords, file)
     