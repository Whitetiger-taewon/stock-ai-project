import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# [설정] 페이지 기본 구성
st.set_page_config(page_title="Stock-AI AX: AI 파동 분석 리포트", layout="wide")

# --- 추가된 구글 시트 저장 함수 ---
def save_to_google_sheet(name, email):
    try:
        # 1. Streamlit Secrets에서 자격 증명 읽기
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Secrets에 설정한 [gcp_service_account] 항목을 불러옵니다.
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        
        # 2. 구글 시트 열기 (본부장님이 만드신 시트 이름과 정확히 일치해야 함)
        # 주의: 서비스 계정 이메일을 이 시트에 '편집자'로 공유하셨어야 합니다.
        sheet = client.open("Stock-AI_Subscribers").sheet1
        
        # 3. 데이터 추가 (날짜, 성함, 이메일)
        sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, email])
        return True
    except Exception as e:
        st.error(f"시트 연동 에러: {e}")
        return False

# 1. 데이터 로딩 자동화 (기존 유지)
@st.cache_data(ttl=3600)
def fetch_real_data(codes):
    results = []
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    for code, name in codes.items():
        try:
            df = fdr.DataReader(code, start_date, end_date)
            if not df.empty and len(df) >= 5:
                prev_close = df.iloc[-5]['Close'] 
                curr_close = df.iloc[-1]['Close'] 
                change = ((curr_close - prev_close) / prev_close) * 100
                results.append({'name': name, 'curr': curr_close, 'change': change})
        except:
            continue
    return results

# --- UI 구현부 ---
st.title("🚀 Stock-AI AX")
st.subheader("12년 IT 전문가의 인사이트와 AI의 결합, '진짜' 변곡점을 배달합니다.")
st.write("단순한 종목 추천이 아닙니다. 엘리어트 파동과 RSI 필터링을 거친 AX 솔루션입니다.")
st.divider()

# B. 실시간 성과 대역 (기존 유지)
st.subheader("📊 지난주 AI 추천 종목 실시간 수익률")
past_targets = {"000660": "SK하이닉스", "005380": "현대차", "035420": "NAVER"}
real_perf = fetch_real_data(past_targets)
cols = st.columns(len(real_perf))
for i, item in enumerate(real_perf):
    cols[i].metric(label=item['name'], 
                   value=f"{item['curr']:,.0f}원", 
                   delta=f"{item['change']:.2f}% (5거래일 대비)")
st.divider()

# C. 이번 주 추천 미리보기 & 구독 섹션
col_left, col_right = st.columns([1.5, 1])
with col_left:
    st.subheader("🎯 이번 주 AI 분석 TOP 3 (미리보기)")
    new_data = [
        {"종목명": "두산에너빌리티", "현재가": "93,600", "AI 타점": "103,488", "상태": "상승3파 진입"},
        {"종목명": "삼성SDI", "현재가": "470,500", "AI 타점": "476,371", "상태": "강력 추세"},
        {"종목명": "한화오션", "현재가": "119,300", "AI 타점": "119,300", "상태": "타점 도달"}
    ]
    st.dataframe(pd.DataFrame(new_data), use_container_width=True)
    st.caption("💡 매주 월요일 아침, 상세 차트 분석 리포트가 발송됩니다.")

with col_right:
    st.subheader("📩 리포트 무료 구독")
    with st.container(border=True):
        st.write("전문가급 HTML 분석 리포트를 받아보세요.")
        u_name = st.text_input("성함", placeholder="홍길동")
        u_email = st.text_input("이메일", placeholder="example@gmail.com")
        
        if st.button("지금 바로 구독 신청", use_container_width=True):
            if u_name and u_email:
                # [수정됨] CSV 저장 대신 구글 시트 저장 함수 호출
                if save_to_google_sheet(u_name, u_email):
                    st.success(f"🎉 {u_name}님, 구독 완료! 정보가 구글 시트에 안전하게 저장되었습니다.")
                    st.balloons()
            else:
                st.warning("정보를 모두 입력해주세요.")

# D. 푸터
st.sidebar.info(f"📍 현재 위치: {datetime.now().strftime('%Y-%m-%d %H:%M')} 기준 갱신 중")
st.sidebar.write("본 서비스는 **AX(AI Transformation)** 기술을 활용한 자산관리 보조 도구입니다.")
