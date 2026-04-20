import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. [설정 영역]
SMTP_SERVER = "smtp.naver.com"
SMTP_PORT = 465
SENDER_EMAIL = "dmstjq2534@naver.com"
# 보안을 위해 GitHub Secrets에 등록한 환경변수를 사용하거나, 직접 입력(테스트용) 하세요.
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '7N7HU227ZKY9') 
RECEIVER_EMAIL = "dmstjq2534@gmail.com"

def create_dynamic_body():
    """엔진이 만든 결과 파일을 읽어서 메일 본문을 생성합니다."""
    try:
        # 엔진이 생성한 파일을 읽습니다 (utf-8 설정 주의)
        if os.path.exists("recommend_results.txt"):
            with open("recommend_results.txt", "r", encoding="utf-8") as f:
                analysis_result = f.read()
        else:
            analysis_result = "⚠️ 분석 결과 파일(recommend_results.txt)이 생성되지 않았습니다."
            
        body = f"""
안녕하세요, 본부장님!
AI 엔진이 분석한 이번 주 엘리어트 파동 추천 리포트입니다.

{analysis_result}

위 결과는 'final_engine_v1.py' 스캔 로직에 의해 자동으로 추출되었습니다.

감사합니다.
Stock-AI KR 자동 리포트 시스템 드림
"""
        return body
    except Exception as e:
        return f"본문 생성 중 에러 발생: {e}"

def send_stock_report():
    # 2. 메일 본문 가져오기 (자동 생성 로직 호출)
    subject = "🚀 [Stock-AI KR] 실시간 AI 추천 종목 리포트"
    body = create_dynamic_body()

    # 3. 메일 객체 생성
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 4. 실제 전송
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"✅ {RECEIVER_EMAIL}로 자동 생성 리포트 전송 성공!")
    except Exception as e:
        print(f"❌ 발송 실패: {e}")

if __name__ == "__main__":
    send_stock_report()
