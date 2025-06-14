import streamlit as st

st.title("app-o3.py の内容")

try:
    with open('app-o3.py', encoding='utf-8') as f:
        code = f.read()
except FileNotFoundError:
    code = 'app-o3.py が見つかりません。'

st.code(code, language='python')