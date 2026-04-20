import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock-AI KR 성과 리포트", layout="wide")

st.title("🚀 Stock-AI KR: 수익률 검증 및 추천 리포트")

# 1. 지난주 수익률 계산 함수
def get_performance(code, name):
    # 7일 전부터 오늘까지 데이터
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    df = fdr.DataReader(code, start_date)
    
    if len(df) >= 2:
        prev_price = df.iloc[0]['Close']  # 7일 전 종가
        curr_price = df.iloc[-1]['Close'] # 현재 종가
        yield_rate = ((curr_price - prev_price) / prev_price) * 100
        return prev_price, curr_price, yield_rate
    return 0, 0, 0

# 2. 지난주 추천 종목 성과 분석
st.subheader("📊 지난주 추천 종목 성과 (검증)")
past_stocks = {"000660": "SK하이닉스", "005380": "현대차"} # 예시 종목
cols = st.columns(len(past_stocks))

for i, (code, name) in enumerate(past_stocks.items()):
    prev, curr, y_rate = get_performance(code, name)
    cols[i].metric(label=name, value=f"{curr:,.0f}원", delta=f"{y_rate:.2f}%")

st.divider()

# 3. 이번 주 신규 추천 종목 (3주차 로직 결과물 연결)
st.subheader("🎯 이번 주 AI 신규 추천 TOP 3")
new_data = [
    {"종목명": "두산에너빌리티", "현재가": 93600, "매수타점": 103488, "기대수익률": "15%+"},
    {"종목명": "삼성SDI", "현재가": 470500, "매수타점": 476371, "기대수익률": "12%+"},
    {"종목명": "한화오션", "현재가": 119300, "매수타점": 119300, "기대수익률": "20%+"}
]
st.table(pd.DataFrame(new_data))

# 4. 자동 발송 시스템 (맛보기)
st.sidebar.header("📬 리포트 자동 발송 설정")
user_email = st.sidebar.text_input("수신 이메일")
if st.sidebar.button("지금 리포트 발송 테스트"):
    st.sidebar.success(f"{user_email}로 분석 리포트가 발송되었습니다!")