import os
import sys
import shutil
import json
import uuid
from datetime import datetime

# 실행 인자 확인
if len(sys.argv) < 2:
    print("사용법: python add_user_gifs.py <user_id>")
    sys.exit(1)

user_id = sys.argv[1].strip()
gifs_src_dir = user_id  # 입력받은 사용자 이름 폴더
dest_gifs_dir = "/opt/mattermost/client/gifs"
dest_thumbs_dir = "/opt/mattermost/client/gifs/thumbnails"
json_file = "users_gifs.json"

# 폴더 확인
if not os.path.isdir(gifs_src_dir):
    print(f"❌ GIF 소스 폴더 '{gifs_src_dir}' 가 존재하지 않습니다.")
    sys.exit(1)

os.makedirs(dest_gifs_dir, exist_ok=True)
os.makedirs(dest_thumbs_dir, exist_ok=True)

# 기존 JSON 불러오기
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        users_data = json.load(f)
else:
    users_data = {}

# 사용자 항목 초기화
if user_id not in users_data:
    users_data[user_id] = []

# GIF 파일 목록
gif_files = [f for f in os.listdir(gifs_src_dir) if f.lower().endswith(".gif")]

for gif_file in gif_files:
    src_path = os.path.join(gifs_src_dir, gif_file)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gif_id = f"{os.path.splitext(gif_file)[0]}_{timestamp}"

    new_filename = f"{user_id}_{gif_id}.gif"
    new_thumb_filename = f"{user_id}_{gif_id}.gif"

    # 복사
    shutil.copy2(src_path, os.path.join(dest_gifs_dir, new_filename))
    shutil.copy2(src_path, os.path.join(dest_thumbs_dir, new_thumb_filename))

    # JSON 데이터 생성
    gif_entry = {
        "id": gif_id,
        "title": os.path.splitext(gif_file)[0],
        "url": f"/static/gifs/{new_filename}",
        "thumbnailUrl": f"/static/gifs/thumbnails/{new_thumb_filename}",
        "tags": ["uploaded", "custom"],
        "userId": user_id
    }
    users_data[user_id].append(gif_entry)

# JSON 저장
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(users_data, f, ensure_ascii=False, indent=2)

print(f"✅ {len(gif_files)}개의 GIF가 '{user_id}' 사용자로 등록되었습니다.")
