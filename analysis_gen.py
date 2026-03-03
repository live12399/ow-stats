import os
import json
import google.generativeai as genai

# 1. Gemini API 설정
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# 가장 안정적인 최신 모델명으로 설정
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def generate_analysis():
    try:
        # 데이터 로드
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if len(history) < 2:
            return "아직 데이터가 충분하지 않습니다. Javis가 데이터를 조금 더 수집할 때까지 기다려 주세요!"

        # 최신 데이터 분석 (전체 티어 기준)
        today_all = history[-1]['data']['all']
        yesterday_all = history[-2]['data']['all']
        
        # 티어별 차이 분석 (브론즈 vs 챔피언 예시)
        bronze_top = history[-1]['data']['bronze'][0]
        champ_top = history[-1]['data']['champion'][0]
        
        changes = []
        for t_hero in today_all[:10]: # 상위 10명 분석
            y_hero = next((h for h in yesterday_all if h['id'] == t_hero['id']), None)
            diff = round(float(t_hero['winRate']) - float(y_hero['winRate']), 2) if y_hero else 0
            changes.append(f"{t_hero['name']}(승률:{t_hero['winRate']}%, 변동:{diff}%)")

        # Javis 페르소나 및 분석 데이터 주입
        prompt = f"""
        당신은 사용자 문태웅의 전용 AI 비서 'Javis'입니다.
        
        오늘의 메타 데이터:
        - 전체 티어 트렌드: {", ".join(changes)}
        - 브론즈 1위: {bronze_top['name']}
        - 챔피언 1위: {champ_top['name']}
        
        위 데이터를 바탕으로 분석 리포트를 작성하세요:
        1. 현재 메타를 지배하는 '압도적 1티어' 영웅은 누구인가?
        2. 브론즈와 상위 티어의 픽 차이에 대한 예리한 분석 한마디.
        3. 문태웅 님을 위한 오늘의 필승 전략 팁.
        
        대답은 ENTP 사용자의 스타일에 맞춰 정중하면서도 명쾌하고, 위트 있게 300자 내외로 작성하세요.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"분석 중 오류 발생: {str(e)}"

# 결과 저장
analysis_result = {"analysis": generate_analysis()}
with open('analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_result, f, ensure_ascii=False, indent=4)

print("✨ Javis가 오늘의 메타 분석을 완료했습니다.")
