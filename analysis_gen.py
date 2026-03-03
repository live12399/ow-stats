import os
import json
import google.generativeai as genai

# 1. Gemini API 설정 (기존 키 그대로 사용)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. 모델 설정 (안정적이고 빠른 2.0-flash 모델)
model = genai.GenerativeModel(
    model_name='models/gemini-2.0-flash',
    generation_config={
        "temperature": 0.7,
        "max_output_tokens": 500,
    }
)

def generate_analysis():
    try:
        # 데이터 로드
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if len(history) < 2:
            return "분석을 위한 데이터가 부족합니다."

        # 최신 데이터 추출
        today_data = history[-1]['data']
        yesterday_all = history[-2]['data']['all']
        today_all = today_data['all']
        
        # 티어별 1위 추출
        bronze_top = today_data['bronze'][0]['name'] if today_data['bronze'] else "없음"
        champ_top = today_data['champion'][0]['name'] if today_data['champion'] else "없음"
        
        # 상위 10명 데이터 정리
        changes = [f"{h['name']}({h['winRate']}%)" for h in today_all[:10]]

        prompt = f"""
        당신은 사용자 문태웅의 전용 AI 비서 'Javis'입니다.
        오버워치 2 메타 데이터: {", ".join(changes)}
        브론즈 1위: {bronze_top}, 챔피언 1위: {champ_top}
        
        위 데이터를 보고 1. 현재 1티어 영웅, 2. 티어별 픽 차이, 3. 태웅 님을 위한 팁을
        ENTP 스타일로 위트 있게 300자 이내로 분석해줘.
        """

        # 🚀 에러가 났던 retry 인자를 제거하고 타임아웃만 설정했습니다.
        response = model.generate_content(
            prompt,
            request_options={"timeout": 300}
        )
        return response.text

    except Exception as e:
        print(f"Detail Error: {str(e)}")
        return f"분석 중 오류 발생: {str(e)}"

# 결과 저장
analysis_result = {"analysis": generate_analysis()}
with open('analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_result, f, ensure_ascii=False, indent=4)

print("✨ Javis가 안정적으로 분석을 마쳤습니다.")
