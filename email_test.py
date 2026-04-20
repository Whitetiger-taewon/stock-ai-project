import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. [설정 영역] 여기서 한 번에 관리하세요!
SMTP_SERVER = "smtp.naver.com"
SMTP_PORT = 465
SENDER_EMAIL = "dmstjq2534@naver.com"   # 본인 네이버 메일 주소
SENDER_PASSWORD = "7N7HU227ZKY9"           # 본인 네이버 비밀번호
RECEIVER_EMAIL = "dmstjq2534@gmail.com"      # 리포트를 받을 메일 주소

def send_stock_report():
    # 2. 메일 본문 작성
    subject = "🚀 [Stock-AI KR] 이번 주 상승 파동 추천 리포트"
    body = """
    안녕하세요, 본부장님!
    AI가 분석한 이번 주 엘리어트 파동 추천 종목입니다.

    1. 두산에너빌리티: 매수타점 103,488원
    2. 삼성SDI: 매수타점 476,371원
    3. 한화오션: 매수타점 119,300원

    성과 검증: 지난주 SK하이닉스(+12.12%) 수익 달성 중!
    
    감사합니다.
    """

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
        print(f"✅ {RECEIVER_EMAIL}로 리포트 전송 성공!")
    except Exception as e:
        print(f"❌ 발송 실패: {e}")

# 5. 실행 명령
if __name__ == "__main__":
    send_stock_report()