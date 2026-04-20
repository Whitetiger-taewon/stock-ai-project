import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# 1. [설정 영역]
SMTP_SERVER = "smtp.naver.com"
SMTP_PORT = 465
SENDER_EMAIL = "dmstjq2534@naver.com"
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '7N7HU227ZKY9')
RECEIVER_EMAIL = "dmstjq2534@gmail.com"

def send_html_newsletter():
    # 메일 객체 설정
    msg = MIMEMultipart('related') # 이미지 삽입을 위해 'related' 타입 사용
    msg['Subject'] = f"🚀 [Stock-AI] 이번 주 AI 추천 종목 리포트 ({datetime.now().strftime('%m/%d')})"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    # HTML 본문 구성 (고급스러운 디자인)
    html_content = """
    <html>
    <body style="font-family: 'Apple SD Gothic Neo', sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px;">📊 AI 파동 분석 리포트</h2>
            <p>안녕하세요, 본부장님! AI 엔진이 포착한 이번 주 최적의 매수 타점 종목입니다.</p>
    """

    # 엔진이 만든 결과 파일 읽기
    if os.path.exists("recommend_results.txt"):
        with open("recommend_results.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            # 종목 정보 추출 (예: [종목명] 현재가: ...)
            stock_name = line.split(']')[0].replace('[', '')
            # 이미지 파일 찾기 (종목코드가 파일명에 포함됨)
            # 여기서는 편의상 엔진에서 저장한 파일 리스트를 가져오는 로직을 가정
            charts = [f for f in os.listdir() if f.startswith('chart_') and f.endswith('.png')]
            
            html_content += f"""
            <div style="margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 10px;">
                <h3 style="margin: 0; color: #222;">🔥 {line.strip()}</h3>
                <div style="margin-top: 15px; text-align: center;">
                    <img src="cid:chart_{i}" style="width: 100%; max-width: 500px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                </div>
            </div>
            """
            
            # 이미지 파일을 메일에 첨부 (메일 내부 참조용)
            if i < len(charts):
                with open(charts[i], 'rb') as img_f:
                    msg_img = MIMEImage(img_f.read())
                    msg_img.add_header('Content-ID', f'<chart_{i}>')
                    msg.attach(msg_img)
    else:
        html_content += "<p>현재 조건에 부합하는 추천 종목이 없습니다.</p>"

    html_content += """
            <div style="margin-top: 40px; font-size: 12px; color: #888; text-align: center;">
                본 리포트는 AI 알고리즘에 의해 자동 생성되었습니다. 투자 판단의 책임은 본인에게 있습니다.
            </div>
        </div>
    </body>
    </html>
    """

    # HTML 본문 추가
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    # 메일 발송
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ 차트가 포함된 HTML 뉴스레터 발송 성공!")
    except Exception as e:
        print(f"❌ 발송 실패: {e}")

if __name__ == "__main__":
    from datetime import datetime
    send_html_newsletter()
