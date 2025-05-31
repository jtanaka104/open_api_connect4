import streamlit as st
from openai import OpenAI

###############################################################################
# Streamlitの「Secrets」からOpenAI API keyを取得
###############################################################################
API_KEY = st.secrets.OpenAIAPI.openai_api_key

###############################################################################
# システムプロンプトの定義（formatはask_ai内で行う）
###############################################################################
system_prompt_for_human = """
あなたはConnect4のAIです。人間（●）の代理として、指定された列に●を落とした新しい盤面を作成してください。

【ルール】
- 盤面は7列×6行です。上から順に表示してください。
- コインは必ず一番下から積み上がります。
- 今回は人間（●）が「{col_num}列目」にコインを落とします。

【出力フォーマット】
- 盤面のみを7列×6行で、上から下へ、1行ずつ「１２３４５６７」から始めて表示してください。
- 盤面以外の説明やコメントは不要です。

現在の盤面:
{b_str}

あなたの番です。新しい盤面を出力してください。
"""

system_prompt_for_ai = """
あなたはConnect4のAIです。AI（×）として、最善の手を選び、盤面を更新してください。

【ルール】
- 盤面は7列×6行です。上から順に表示してください。
- コインは必ず一番下から積み上がります。
- 今回はあなた（×）の番です。

【出力フォーマット】
- 盤面のみを7列×6行で、上から下へ、1行ずつ「１２３４５６７」から始めて表示してください。
- 盤面以外の説明やコメントは不要です。

現在の盤面:
{b_str}

あなたの番です。新しい盤面を出力してください。
"""

###############################################################################
# セッション初期化
###############################################################################
def init_board_str():
    return "１２３４５６７\n□□□□□□□\n□□□□□□□\n□□□□□□□\n□□□□□□□\n□□□□□□□\n□□□□□□□"

if "board_str" not in st.session_state:
    st.session_state["board_str"] = init_board_str()
    st.session_state["turn"] = "human"
    st.session_state["message"] = ""
    st.session_state["gameover"] = False
    st.session_state["last_move"] = None

###############################################################################
# AIへの問い合わせ
###############################################################################
def ask_ai(board_str, last_move=None, player="ai"):
    if player == "human":
        if last_move is None:
            return None
        prompt = system_prompt_for_human.format(b_str=board_str, col_num=last_move+1)
    else:
        prompt = system_prompt_for_ai.format(b_str=board_str)

    print(prompt)
    ###############################################
    # gpt-3.5-turbo input: $0.50 output: $1.50
    # gpt-4o-mini   input: $0.15 output: $0.60
    # o1            input:$15.00 output:$60.00
    # o3            input:$10.00 output:$40.00
    ###############################################
    # gpt-3.5-turbo < gpt-4o-mini < o1 < o3
    ###############################################
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    import re
    content = response.choices[0].message.content
    print(content)
    match = re.search(r"１２３４５６７\n([□×●\n]{42,})", content)
    if match:
        board_str = "１２３４５６７\n" + match.group(1).strip()
        return board_str
    else:
        return None

###############################################################################
# ユーザーインターフェイスの構築
###############################################################################
st.title("Connect4（盤面生成版）")
st.write(st.session_state["board_str"].replace("\n", "<br/>"), unsafe_allow_html=True)

if not st.session_state["gameover"]:
    if st.session_state["turn"] == "human":
        st.session_state["message"] = ""
        with st.form(key="user_form", clear_on_submit=True):
            col = st.text_input("あなたの番です。1-7の数字を入力してください。", key="user_input")
            submitted = st.form_submit_button("決定")
        if submitted and col and col.isdigit() and 1 <= int(col) <= 7:
            col_idx = int(col) - 1
            new_board = ask_ai(st.session_state["board_str"], last_move=col_idx, player="human")
            if new_board:
                st.session_state["board_str"] = new_board
                st.session_state["turn"] = "ai"
                st.session_state["last_move"] = col_idx
            else:
                st.session_state["message"] = "AIが不正な盤面を返しました。"
            st.rerun()
        elif submitted:
            st.session_state["message"] = "1から7の数字を入力してください。"
            st.rerun()
    elif st.session_state["turn"] == "ai":
        st.text_input("", key="user_input", value="", disabled=True, label_visibility="collapsed")
        st.session_state["message"] = "AIの番です。考え中..."
        st.write(st.session_state["message"])
        new_board = ask_ai(st.session_state["board_str"], last_move=st.session_state["last_move"], player="ai")
        if new_board:
            st.session_state["board_str"] = new_board
            st.session_state["turn"] = "human"
        else:
            st.session_state["message"] = "AIが不正な盤面を返しました。"
        st.rerun()

if st.session_state["message"]:
    st.write(st.session_state["message"])

if st.button("リセット"):
    st.session_state["board_str"] = init_board_str()
    st.session_state["turn"] = "human"
    st.session_state["message"] = ""
    st.session_state["gameover"] = False
    st.session_state["last_move"] = None
    st.rerun()

