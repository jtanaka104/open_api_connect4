import streamlit as st

st.title("app-o1-mini.py の内容")

try:
    with open('app-o1-mini.py', encoding='utf-8') as f:
        code = f.read()
except FileNotFoundError:
    code = 'app-o1-mini.py が見つかりません。'

st.code(code, language='python')