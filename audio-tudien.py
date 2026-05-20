import requests
import json
import time
import os

# ==========================================
# CẤU HÌNH THÔNG TIN
# ==========================================
API_KEY = "sk-api-CFWXd5-8DQcs37gVkBlEJWPsXa6dtNeP7VprDm9umf_lBVJciH8JOuBBg3XpMA05xBAaTosz4vkB2tidsCR5XEVILBBaA0pdLWORQXrMJNZlTbmrl4b1W2g"
GROUP_ID = "1923652080648589412"

# ID Giọng đọc
VOICE_NU_ID = "moss_audio_3d3480a1-37b9-11f0-b6c4-9e15325fe584" 
VOICE_NAM_ID = "moss_audio_fa7b179e-3b88-11f0-9641-faec05e4a37f"

# Tạo thư mục
os.makedirs("audio_tudien/nu", exist_ok=True)
os.makedirs("audio_tudien/nam", exist_ok=True)

url = f"https://api.minimax.io/v1/t2a_v2?GroupId={GROUP_ID}"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Hàm gọi API lấy âm thanh
def get_audio(word, voice_id, output_path):
    if os.path.exists(output_path):
        return True # Đã tải rồi thì bỏ qua ngay lập tức
        
    payload = {
        "model": "speech-2.8-hd",
        "text": word,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": 1.0, 
            "vol": 1.0,
            "pitch": 0
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3"
        }
    }
    
    while True:
        try:
            # ĐÃ THÊM TIMEOUT=15: Chống treo máy khi rớt mạng/đổi wifi
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get("base_resp", {}).get("status_code") == 0:
                hex_audio = response_data.get("data", {}).get("audio", "")
                if hex_audio:
                    with open(output_path, "wb") as f:
                        f.write(bytes.fromhex(hex_audio))
                    return True
            
            elif response.status_code == 429 or response_data.get("base_resp", {}).get("status_code") in [1004, 1005]:
                print("⏳ Quá nhanh, đợi xíu...", end=" ")
                time.sleep(2)
                continue
            else:
                print(f"❌ Lỗi API: {response_data}")
                return False
                
        except Exception as e:
            # Bắt mọi lỗi rớt mạng, treo mạng và tự động chạy lại
            print("⏳ Mạng chập chờn, tự động thử lại...", end=" ")
            time.sleep(2)

# ==========================================
# THỰC THI ĐỌC FILE JSON
# ==========================================
try:
    with open('tu-dien.json', 'r', encoding='utf-8') as f:
        tu_dien = json.load(f)
except FileNotFoundError:
    print("❌ Không tìm thấy file tu-dien.json ở thư mục hiện tại!")
    exit()

words = list(tu_dien.keys())
print(f"Bắt đầu xử lý {len(words)} từ vựng...")

for index, word in enumerate(words):
    # Chỉ in ra màn hình những từ đang thực sự phải tải, từ nào có rồi nó lướt qua luôn
    path_nu = f"audio_tudien/nu/{word}.mp3"
    path_nam = f"audio_tudien/nam/{word}.mp3"
    
    if os.path.exists(path_nu) and os.path.exists(path_nam):
        continue # Lướt qua như một cơn gió
        
    print(f"[{index + 1}/{len(words)}] Đang tải: {word}...", end=" ")
    
    success_nu = get_audio(word, VOICE_NU_ID, path_nu)
    success_nam = get_audio(word, VOICE_NAM_ID, path_nam)
    
    if success_nu and success_nam:
        print("✅ Xong!")
    else:
        print("❌ Lỗi, bỏ qua từ này!")

print("\n🎉 HOÀN THÀNH TẤT CẢ! Hãy copy thư mục 'audio_tudien' bỏ vào public của web.")