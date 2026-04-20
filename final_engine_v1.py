import FinanceDataReader as fdr
from scipy.signal import find_peaks
import pandas as pd
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 리눅스 서버에 설치된 나눔 폰트 경로 지정
font_path = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'
font_prop = fm.FontProperties(fname=font_path)

# 전역 폰트 설정
plt.rc('font', family='NanumBarunGothic')

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# RSI 지표 계산 함수 (고도화 단계: 기술적 분석 강화)
def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_stock(stock_code, stock_name):
    try:
        # 1. 데이터 수집 (최근 1년)
        df = fdr.DataReader(stock_code, (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
        if len(df) < 100: return None

        # 고도화: RSI 계산 및 현재 RSI 추출
        df['RSI'] = calculate_rsi(df)
        current_rsi = df['RSI'].iloc[-1]

        # 2. 변곡점 추출 (엘리어트 파동 기초)
        peaks, _ = find_peaks(df['High'], distance=20)
        troughs, _ = find_peaks(-df['Low'], distance=20)
        pts = pd.concat([pd.Series(peaks), pd.Series(troughs)]).sort_values()
        wave_points = df.iloc[pts]

        if len(wave_points) < 5: return None
        
        p = wave_points.tail(5)['Close'].values
        p1, p2, p3, p4, p5 = p[0], p[1], p[2], p[3], p[4]

        # 3. 규칙 검증 (고도화: 엘리어트 파동 + RSI 필터링)
        rule1 = p2 > p1 * 0.95 
        rule2 = (p4 - p3) > (p2 - p1)
        rule3 = current_rsi < 70 # 과매수 구간 제외 (안정성 강화)

        if rule1 and rule2 and rule3:
            # 4. 피보나치 매수 타점 계산
            recent_high = max(p3, p5)
            recent_low = p4
            diff = recent_high - recent_low
            buy_target = recent_high - (diff * 0.618)
            
            # 시각화: 차트 생성 및 저장
            create_analysis_chart(df, stock_code, stock_name, buy_target)
            
            return {
                '종목코드': stock_code,
                '종목명': stock_name,
                '현재가': p5,
                '매수권장가': round(buy_target),
                'RSI': round(current_rsi, 1),
                '상태': '상승파동 확인'
            }
    except:
        return None

def create_analysis_chart(df, code, name, buy_target):
    """시각화: 분석 차트 생성 함수"""
    plt.figure(figsize=(10, 6))
    plt.plot(df.index[-60:], df['Close'][-60:], label='Price', color='royalblue')
    plt.axhline(y=buy_target, color='crimson', linestyle='--', label=f'Buy Target ({buy_target:,.0f})')
    plt.title(f"AI Analysis: {name} ({code})", fontsize=15)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 이미지 저장 (수익화 시 이메일에 첨부될 핵심 리소스)
    plt.savefig(f"chart_{code}.png")
    plt.close()

# --- 메인 실행부 ---
print("--- [Stock-AI KR] V2.0 고도화 스캔 시작 ---")
# 상위 종목 리스트 확보
kospi_list = fdr.StockListing('KOSPI').head(100) 
recommend_list = []

for index, row in kospi_list.iterrows():
    print(f"분석 중: {row['Name']} ({row['Code']})...", end='\r')
    result = analyze_stock(row['Code'], row['Name'])
    if result:
        recommend_list.append(result)
    time.sleep(0.1)

print("\n" + "="*50)
print(f"스캔 완료! 최종 추천 종목: {len(recommend_list)}개")
print("="*50)

save_lines = []
for rec in recommend_list:
    line_info = f"[{rec['종목명']}] 현재가: {rec['현재가']:,}원 | RSI: {rec['RSI']} | ★매수타점: {rec['매수권장가']:,}원"
    print(line_info)
    save_lines.append(line_info)

with open("recommend_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(save_lines))

print("\n✅ 추천 리포트 및 분석 차트 생성 완료.")
