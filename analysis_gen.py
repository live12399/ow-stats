import os
import json
import google.generativeai as genai

# 1. Gemini API 설정
# GitHub Secrets에 등록된 키를 사용합니다.
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. 모델 설정 (404 에러 방지를 위해 명시적인 최신 모델명 사용)
# 'gemini-1.5-flash' 대신 '-latest'를 붙이는 것이 가장 안전합니다.
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def generate_analysis():
    try:
        # 데이터 로드 (역사적 데이터와 현재 데이터 비교)
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 데이터가 최소 2개(오늘, 어제)는 있어야 변동폭 분석이 가능합니다.
        if len(history) < 2:
            return "분석을 위한 데이터가 쌓이고 있습니다. Javis가 충분한 정보를 수집할 때까지 조금만 기다려 주세요!"

        # 최신 데이터 추출
        today_data = history[-1]['data']
        yesterday_all = history[-2]['data']['all']
        
        # 티어별 핵심 데이터 추출 (브론즈와 챔피언 비교)
        today_all = today_data['all']
        bronze_top = today_data['bronze'][0] if today_data['bronze'] else {"name": "기록 없음"}
        champ_top = today_data['champion'][0] if today_data['champion'] else {"name": "기록 없음"}
        
        # 상위 10명 영웅의 전날 대비 승률 변동 계산
        changes = []
        for t_hero in today_all[:10]:
            y_hero = next((h for h in yesterday_all if h['id'] == t_hero['id']), None)
            diff = round(float(t_hero['winRate']) - float(y_hero['winRate']), 2) if y_hero else 0
            changes.append(f"{t_hero['name']}(승률:{t_hero['winRate']}%, 변동:{diff}%)")

        # Javis 페르소나 및 분석 프롬프트 구성
        prompt = f"""
        당신은 사용자 문태웅의 전용 AI 비서 'Javis'입니다.
        
        오늘의 오버워치 2 티어별 메타 데이터입니다:
        - 전체 트렌드: {", ".join(changes)}
        - 브론즈(Bronze) 1위 영웅: {bronze_top['name']}
        - 챔피언(Champion) 1위 영웅: {champ_top['name']}
        
        이 데이터를 바탕으로 리포트를 작성하세요:
        1. 현재 모든 티어에서 압도적인 '메타 파괴자' 영웅 분석.
        2. 하위 티어와 최상위 티어 간의 픽 차이에 대한 예리한 통찰.
        3. 문태웅 님을 위한 오늘의 추천 영웅과 플레이 팁.
        
        ENTP 사용자의 성향에 맞춰 정중하면서도 명쾌하고, 위트 있는 말투로 350자 내외로 작성해줘.
        """

        # Gemini 모델을 통한 텍스트 생성
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # 에러 발생 시 로그를 남겨 디버깅을 돕습니다.
        print(f"Detail Error: {str(e)}")
        return f"분석 중 오류 발생: {str(e)}"

# 3. 결과 저장 (웹사이트의 index.html에서 이 파일을 읽습니다)
analysis_result = {"analysis": generate_analysis()}
with open('analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_result, f, ensure_ascii=False, indent=4)

print("✨ Javis가 성공적으로 티어별 메타 리포트를 업데이트했습니다.")
