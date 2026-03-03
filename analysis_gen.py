import os
import json
import google.generativeai as genai
from google.api_core import retry

# 1. Gemini API 설정
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. 모델 설정 (Gemini 3 프리뷰 모델 사용 및 최적화)
model = genai.GenerativeModel(
    model_name='models/gemini-3-flash-preview',
    generation_config={
        "temperature": 0.7,
        "max_output_tokens": 800, # 답변 길이를 적절히 제한해 속도 향상
    }
)

def generate_analysis():
    try:
        # 데이터 로드
        if not os.path.exists('history.json'):
            return "역사 데이터 파일이 없습니다."
            
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if len(history) < 2:
            return "분석을 위한 데이터가 쌓이고 있습니다. Javis가 정보를 더 수집할 때까지 기다려 주세요!"

        # 최신 데이터 및 이전 데이터 추출
        today_data = history[-1]['data']
        yesterday_all = history[-2]['data']['all']
        
        today_all = today_data['all']
        bronze_top = today_data['bronze'][0] if today_data['bronze'] else {"name": "기록 없음"}
        champ_top = today_data['champion'][0] if today_data['champion'] else {"name": "기록 없음"}
        
        # 승률 변동 계산 (상위 10명)
        changes = []
        for t_hero in today_all[:10]:
            y_hero = next((h for h in yesterday_all if h['id'] == t_hero['id']), None)
            try:
                t_win = float(t_hero['winRate'])
                y_win = float(y_hero['winRate']) if y_hero else t_win
                diff = round(t_win - y_win, 2)
            except:
                diff = 0
                t_win = t_hero['winRate']
            changes.append(f"{t_hero['name']}(승률:{t_win}%, 변동:{diff}%)")

        # Javis 페르소나 주입
        prompt = f"""
        당신은 사용자 문태웅의 전용 AI 비서 'Javis'입니다.
        
        오늘의 오버워치 2 티어별 메타 데이터:
        - 전체 트렌드: {", ".join(changes)}
        - 브론즈(Bronze) 1위 영웅: {bronze_top['name']}
        - 챔피언(Champion) 1위 영웅: {champ_top['name']}
        
        이 데이터를 바탕으로 리포트를 작성하세요:
        1. 현재 모든 티어에서 압도적인 '메타 파괴자' 영웅 분석.
        2. 하위 티어와 최상위 티어 간의 픽 차이에 대한 예리한 통찰.
        3. 문태웅 님을 위한 오늘의 추천 영웅과 플레이 팁.
        
        ENTP 사용자의 스타일에 맞춰 정중하면서도 위트 있고 명쾌하게 350자 내외로 작성해줘.
        """

        # 🚀 핵심: 대기 시간을 600초로 늘려 504 Deadline expired 에러 방지
        response = model.generate_content(
            prompt,
            request_options={"timeout": 600}
        )
        return response.text

    except Exception as e:
        print(f"Detail Error: {str(e)}")
        return f"분석 중 오류 발생: {str(e)}"

# 3. 결과 저장 및 실행
analysis_result = {"analysis": generate_analysis()}
with open('analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_result, f, ensure_ascii=False, indent=4)

print("✨ Javis가 타임아웃 방지 설정을 적용하여 분석을 완료했습니다.")
