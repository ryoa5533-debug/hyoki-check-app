import streamlit as st
import pandas as pd
import re
from datetime import datetime
import pytesseract
from pdf2image import convert_from_bytes
import io 

st.title("📘 表記便覧・文書事務手引 文書チェックアプリ")

# =========================

ルール読み込み

# =========================

st.sidebar.header("① ルール設定")

hyoki_file = st.sidebar.file_uploader("表記便覧Excel（正表記・NG表記）", type=["xlsx"])

rules = None
if hyoki_file:
    rules = pd.read_excel(hyoki_file)
    st.sidebar.success(f"ルール読込: {len(rules)}件")
# =========================

文書アップロード

# =========================

st.header("② 文書アップロード")

uploaded = st.file_uploader("PDF または 画像", type=["pdf","png","jpg","jpeg"])

# =========================

OCR関数

# =========================

def ocr_pdf(file_bytes):
    images = convert_from_bytes(file_bytes)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang="jpn")
    return text

# =========================

曜日チェック

# =========================

def weekday_check(text):
    results = []
    pattern = r"(\d{4}/\d{1,2}/\d{1,2})（([月火水木金土日])）"

    import re
    from datetime import datetime

    for m in re.finditer(pattern, text):
        date_str = m.group(1)
        w = m.group(2)

        try:
            d = datetime.strptime(date_str, "%Y/%m/%d")
            real = "月火水木金土日"[d.weekday()]
            if real != w:
                results.append(f"{date_str}（{w}）→ 正:{real}")
        except:
            pass

    return results

# =========================

表記チェック

# =========================

def hyoki_check(text, rules_df):
    results = []

    if rules_df is None:
        return results

    for _, r in rules_df.iterrows():
        ng = str(r[0])
        ok = str(r[1])

        if ng in text:
            results.append(f"{ng} → {ok}")

    return results

# =========================

番号チェック

# =========================

def number_check(text):
    results = []

    nums = re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩]", text)
    order = "①②③④⑤⑥⑦⑧⑨⑩"

    prev = -1
    for n in nums:
        idx = order.find(n)

        if prev != -1 and idx != prev + 1:
            results.append(f"{order[prev]}の次が{n}")

        prev = idx

    return results

# =========================

チェック実行

# =========================

if st.button("③ チェック実行"):

    if uploaded and rules is not None:

        bytes_data = uploaded.read()

        if uploaded.type == "application/pdf":
            text = ocr_pdf(bytes_data)
        else:
            text = ocr_image(bytes_data)

        st.subheader("抽出テキスト")
        st.text_area("", text, height=200)

        st.subheader("④ チェック結果")

        res = []
        res += hyoki_check(text, rules)
        res += weekday_check(text)
        res += number_check(text)

        if res:
            for r in res:
                st.warning(r)
        else:
            st.success("問題なし")

if uploaded.type == "application/pdf":
        text = ocr_pdf(bytes_data)
    else:
        text = ocr_image(bytes_data)

    st.subheader("抽出テキスト")
    st.text_area("", text, height=200)

    st.subheader("④ チェック結果")

    res = []
    res += hyoki_check(text, rules)
    res += weekday_check(text)
    res += number_check(text)

    if res:
        for r in res:
            st.warning(r)
    else:
        st.success("エラーなし")

else:
    st.error("ルールExcelと文書をアップしてください")?
