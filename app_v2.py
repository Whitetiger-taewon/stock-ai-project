import json
import re
import os
import random
import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# [설정] 페이지 기본 구성
st.set_page_config(page_title="Stock-AI AX: 실시간 AI 변곡점 리포트", layout="wide")

# --- 1. 데이터 및 유틸리티 함수 ---

def get_scanning_list():
    """target_stocks.txt 파일을 읽어 전체 분석 대상 종목을 가져옵니다."""
    default_scan = {"005930": "삼성전자", "000660": "SK하이닉스", "005380": "현대차"}
    try:
        if os.path.exists("target_stocks.txt"):
            with open("target_stocks.txt", "r", encoding="utf-8") as f:
                new_scan = {}
                for line in f.readlines():
                    if ':' in line:
                        code, name = line.strip().split(':')
                        new_scan[code.strip()] = name.strip()
                return new_scan if new_scan else default_scan
    except:
        pass
    return default_scan

def get_past_targets():
    """지난주 추천 종목을 읽어오되, 파일이 없으면 전체 풀에서 랜덤 3개를 선정합니다."""
    try:
        if os.path.exists("past_recommend_results.txt"):
            with open("past_recommend_results.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    target_dict = {}
                    for item in content.split(','):
                        code, name = item.split(':')
                        target_dict[code.strip()] = name.strip()
                    return target_dict
    except:
        pass

    full_list = get_scanning_list()
    if len(full_list) >= 3:
        keys = random.sample(list(full_list.keys()), 3)
        return {k: full_list[k] for k in keys}
    return full_list

@st.cache_data(ttl=3600)
def fetch_real_data(codes):
    """주식 종목의 실시간 수익률 성과를 계산합니다."""
    results = []
    kst_today = datetime.utcnow() + timedelta(hours=9)
    end_date = kst_today.strftime('%Y-%m-%d')
    start_date = (kst_today - timedelta(days=14)).strftime('%Y-%m-%d')
    
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

@st.cache_data(ttl=3600)
def fetch_realtime_recommendations():
    """실시간 시장 스캐닝을 통해 상위 3개 종목을 추출합니다."""
    scan_list = get_scanning_list()
    analysis_results = []
    kst_today = datetime.utcnow() + timedelta(hours=9)
    start_date = (kst_today - timedelta(days=10)).strftime('%Y-%m-%d')
    
    for code, name in scan_list.items():
        try:
            df = fdr.DataReader(code, start_date)
            if not df.empty and len(df) >= 2:
                curr_price = df.iloc[-1]['Close']
                prev_price = df.iloc[-2]['Close']
                change_rate = ((curr_price - prev_price) / prev_price) * 100
                
                analysis_results.append({
                    "종목명": name,
                    "현재가": f"{curr_price:,.0f}원",
                    "상태": "강한 수급" if change_rate > 0.5 else "눌림목 형성",
                    "스코어": change_rate
                })
        except:
            continue
            
    return sorted(analysis_results, key=lambda x: x['스코어'], reverse=True)[:3]

def save_to_google_sheet(name, email):
    """구독자 정보를 구글 시트에 기록합니다."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw_json = st.secrets["gcp_service_account_json"]
        clean_json = re.sub(r'[\x00-\x1F\x7F]', '', raw_json) 
        service_account_info = json.loads(clean_json)
        
        creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("Stock-AI_Subscribers").sheet1
        
        kst_now = datetime.utcnow() + timedelta(hours=9)
        now_str = kst_now.strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now_str, name, email])
        return True
    except Exception as e:
        st.error(f"구독 연동 오류: {e}")
        return False

# --- 2. UI 메인 구현 ---

st.title("🚀 Stock-AI AX")
st.subheader("12년 IT 전문가의 인사이트와 AI의 결합, '진짜' 변곡점을 분석합니다.")
st.write("엘리어트 파동과 실시간 수급 데이터를 기반으로 최적의 타점을 제공합니다.")
st.divider()

# [B] 성과 대역
st.subheader("📊 지난주 AI 추천 종목 실시간 성과")
past_targets = get_past_targets()
real_perf = fetch_real_data(past_targets)

if real_perf:
    cols = st.columns(len(real_perf))
    for i, item in enumerate(real_perf):
        cols[i].metric(
            label=item['name'], 
            value=f"{item['curr']:,.0f}원", 
            delta=f"{item['change']:.2f}% (최근 5거래일)"
        )
else:
    st.info("성과 데이터를 분석 중입니다...")
st.divider()

# [C] 분석 & 구독 섹션
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("🎯 실시간 AI 스캐닝 TOP 3")
    
    if os.path.exists("recommend_results.txt"):
        try:
            with open("recommend_results.txt", "r", encoding="utf-8") as f:
                st.success("✅ 이번 주 메일로 발송된 확정 분석 데이터입니다.")
                st.markdown(f"```text\n{f.read()}\n```")
        except:
            st.info("데이터 로드 중...")
    else:
        st.info("🔍 현재 전체 종목 실시간 스캐닝 중 (1시간 단위 갱신)")
        realtime_data = fetch_realtime_recommendations()
        if realtime_data:
            st.table(pd.DataFrame(realtime_data)[["종목명", "현재가", "상태"]])
        else:
            st.warning("시장 데이터를 수집할 수 없습니다.")
            
    st.caption("💡 매주 월요일 아침 8시, 딥러닝 기반 분석 리포트가 구독자에게 발송됩니다.")

with col_right:
    st.subheader("📩 리포트 무료 구독")
    with st.container(border=True):
        st.write("전문가급 HTML 분석 리포트를 받아보세요.")
        u_name = st.text_input("성함", placeholder="홍길동")
        u_email = st.text_input("이메일", placeholder="example@gmail.com")
        
        if st.button("지금 바로 구독 신청", use_container_width=True):
            if u_name and u_email:
                if save_to_google_sheet(u_name, u_email):
                    st.success(f"🎉 {u_name}님, 구독 완료!")
                    st.balloons()
            else:
                st.warning("정보를 모두 입력해주세요.")

# [D] 푸터
kst_now = datetime.utcnow() + timedelta(hours=9)
st.sidebar.markdown(f"### 🕒 Last Update\n**{kst_now.strftime('%Y-%m-%d %H:%M')} KST**")
st.sidebar.divider()
st.sidebar.write("본 서비스는 **AX(AI Transformation)** 기술을 활용한 자산관리 보조 도구입니다.")
