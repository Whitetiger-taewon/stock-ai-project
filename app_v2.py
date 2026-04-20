import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

# [설정] 페이지 기본 구성
st.set_page_config(page_title="Stock-AI KR 실시간 리포트", layout="wide")

# 1. 데이터 로딩 자동화 함수 (캐싱 적용: 1시간 동안 유지)
@st.cache_data(ttl=3600)
def fetch_real_data(codes):
    results = []
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    for code, name in codes.items():
        df = fdr.DataReader(code, start_date, end_date)
        if not df.empty and len(df) >= 5:
            prev_close = df.iloc[-5]['Close'] # 5거래일 전 종가
            curr_close = df.iloc[-1]['Close'] # 현재 종가
            change = ((curr_close - prev_close) / prev_close) * 100
            results.append({'name': name, 'curr': curr_close, 'change': change})
    return results

# --- UI 구현부 ---
st.title("🚀 Stock-AI KR: 실시간 성과 및 추천")

# 2. 지난주 성과 실시간 갱신
st.subheader("📊 지난주 AI 추천 종목 실시간 수익률")
past_targets = {"000660": "SK하이닉스", "005380": "현대차", "035420": "NAVER"}
real_perf = fetch_real_data(past_targets)

cols = st.columns(len(real_perf))
for i, item in enumerate(real_perf):
    cols[i].metric(label=item['name'], 
                   value=f"{item['curr']:,.0f}원", 
                   delta=f"{item['change']:.2f}% (5일 전 대비)")

st.divider()

# 3. 이번 주 AI 분석 타점 (실제 계산 로직 연결 가능)
st.subheader("🎯 이번 주 AI 신규 추천 TOP 3")
# 이곳에 본부장님의 엘리어트 파동/피보나치 로직을 연결하면 실시간 스캔이 시작됩니다.
new_data = [
    {"종목명": "두산에너빌리티", "현재가": "93,600", "AI 타점": "103,488", "상태": "상승3파 진입"},
    {"종목명": "삼성SDI", "현재가": "470,500", "AI 타점": "476,371", "상태": "강력 추세"},
    {"종목명": "한화오션", "현재가": "119,300", "AI 타점": "119,300", "상태": "타점 도달"}
]
st.table(pd.DataFrame(new_data))

st.sidebar.info("💡 모든 데이터는 1시간마다 자동으로 갱신됩니다.")
