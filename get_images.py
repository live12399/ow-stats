import requests
import os

def download_hero_images():
    # 1. 이미지를 저장할 폴더 만들기
    if not os.path.exists('images'):
        os.makedirs('images')
        print("📁 'images' 폴더를 생성했습니다.")

    # 2. 오버워치 API에서 영웅 목록 가져오기 (OverFast API 사용)
    print("🌐 영웅 데이터를 조회 중입니다...")
    url = "https://overfast-api.tekrop.fr/heroes"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        heroes = response.json()
        
        print(f"총 {len(heroes)}명의 영웅을 발견했습니다. 다운로드를 시작합니다!")

        # 3. 각 영웅의 이미지 다운로드
        for hero in heroes:
            key = hero['key']  # 예: kiriko, tracer
            image_url = hero['portrait'] # 초상화 주소
            
            # 이미지 파일 저장 (예: images/kiriko.png)
            img_data = requests.get(image_url).content
            with open(f'images/{key}.png', 'wb') as handler:
                handler.write(img_data)
            
            print(f"✅ 다운로드 완료: {key}")

        print("\n🎉 모든 이미지 다운로드가 끝났습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    download_hero_images()