import os
import json
import google.generativeai as genai

# 1. GitHub Secrets에서 키 가져오기
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# 기존에 사용하시던 유료 티어 모델을 그대로 사용합니다.
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_analysis():
    try:
        # 데이터 로드
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if len(history) < 2:
            return "분석을 위한 데이터가 부족합니다. 점이 더 찍힐 때까지 기다려주세요!"

        # 최신 데이터와 이전 데이터 비교
        today = history[-1]['data']['all']
        yesterday = history[-2]['data']['all']
        
        changes = []
        for t_hero in today[:10]: # 상위 10명 분석
            y_hero = next((h for h in yesterday if h['id'] == t_hero['id']), None)
            diff = round(float(t_hero['winRate']) - float(y_hero['winRate']), 2) if y_hero else 0
            changes.append(f"{t_hero['name']}({t_hero['winRate']}%, 변동:{diff}%)")

        # Javis 페르소나 주입
        prompt = f"""
        너는 사용자 문태웅의 전용 AI 비서 'Javis'야.
        오늘의 오버워치 2 승률 데이터야: {", ".join(changes)}
        
        이 데이터를 보고 분석해줘:
        1. 현재 가장 '사기 캐릭터'라고 볼 수 있는 영웅 1~2명.
        2. 승률이 급격히 변한 영웅에 대한 한마디.
        3. 문태웅 님에게 드리는 오늘의 플레이 팁.
        
        대답은 비서답게 정중하면서도 명확하게 300자 내외로 해줘.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"분석 중 오류 발생: {str(e)}"

# 결과 저장
analysis_result = {"analysis": generate_analysis()}
with open('analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_result, f, ensure_ascii=False, indent=4)
