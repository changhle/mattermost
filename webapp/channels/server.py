# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import json
# import base64
# import os
# from typing import List, Dict, Any
# import uuid
# from datetime import datetime

# app = Flask(__name__)
# CORS(app)  # CORS 설정 (프론트엔드와 연결을 위해)

# # 설정
# JSON_FILE_PATH = 'gifs.json'
# GIF_DIRECTORY = './public/gifs'
# THUMBNAIL_DIRECTORY = './public/gifs/thumbnails'

# # 디렉토리 생성
# # os.makedirs(GIF_DIRECTORY, exist_ok=True)
# # os.makedirs(THUMBNAIL_DIRECTORY, exist_ok=True)

# # LocalGif 타입 정의
# class LocalGif:
#     def __init__(self, id: str, title: str, url: str, thumbnailUrl: str, tags: List[str]):
#         self.id = id
#         self.title = title
#         self.url = url
#         self.thumbnailUrl = thumbnailUrl
#         self.tags = tags
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             'id': self.id,
#             'title': self.title,
#             'url': self.url,
#             'thumbnailUrl': self.thumbnailUrl,
#             'tags': self.tags
#         }

# # 기본 GIF 데이터
# DEFAULT_LOCAL_GIFS = [
#     {
#         'id': '1',
#         'title': 'Happy',
#         'url': '/gifs/happy.gif',
#         'thumbnailUrl': '/gifs/thumbnails/happy.gif',
#         'tags': ['happy', 'smile', 'joy']
#     },
#     {
#         'id': '2',
#         'title': 'Thumbs Up',
#         'url': '/gifs/thumbs-up.gif',
#         'thumbnailUrl': '/gifs/thumbnails/thumbs-up.gif',
#         'tags': ['thumbs', 'up', 'good', 'approve']
#     },
#     {
#         'id': '3',
#         'title': 'Clap',
#         'url': '/gifs/clap.gif',
#         'thumbnailUrl': '/gifs/thumbnails/clap.gif',
#         'tags': ['clap', 'applause', 'good job']
#     }
# ]

# def load_gifs() -> List[Dict[str, Any]]:
#     """JSON 파일에서 GIF 목록을 로드"""
#     try:
#         if os.path.exists(JSON_FILE_PATH):
#             with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         else:
#             # 파일이 없으면 기본 데이터로 초기화
#             save_gifs(DEFAULT_LOCAL_GIFS)
#             return DEFAULT_LOCAL_GIFS
#     except Exception as e:
#         print(f"GIF 로드 중 오류: {e}")
#         return DEFAULT_LOCAL_GIFS

# def save_gifs(gifs: List[Dict[str, Any]]) -> bool:
#     """GIF 목록을 JSON 파일에 저장"""
#     try:
#         with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
#             json.dump(gifs, f, ensure_ascii=False, indent=2)
#         return True
#     except Exception as e:
#         print(f"GIF 저장 중 오류: {e}")
#         return False

# def save_base64_to_file(base64_data: str, filename: str) -> bool:
#     """base64 데이터를 파일로 저장"""
#     try:
#         # base64 헤더 제거 (data:image/gif;base64, 부분)
#         if ',' in base64_data:
#             base64_data = base64_data.split(',')[1]
        
#         # base64 디코딩
#         gif_data = base64.b64decode(base64_data)
        
#         # 파일 저장
#         with open(filename, 'wb') as f:
#             f.write(gif_data)
        
#         return True
#     except Exception as e:
#         print(f"파일 저장 중 오류: {e}")
#         return False

# @app.route('/gifs', methods=['GET'])
# def get_gifs():
#     """GIF 목록 반환"""
#     try:
#         gifs = load_gifs()
#         return jsonify({
#             'success': True,
#             'data': gifs,
#             'count': len(gifs)
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/gifs', methods=['POST'])
# def add_gif():
#     """새 GIF 추가"""
#     try:
#         data = request.json
        
#         # 필수 필드 확인
#         required_fields = ['title', 'tags']
#         for field in required_fields:
#             if field not in data:
#                 return jsonify({
#                     'success': False,
#                     'error': f'필수 필드 누락: {field}'
#                 }), 400
        
#         # 고유 ID 생성
#         gif_id = data.get('id', str(uuid.uuid4()))
        
#         # 파일명 생성
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"{gif_id}_{timestamp}.gif"
#         thumbnail_filename = f"{gif_id}_{timestamp}_thumb.gif"
        
#         gif_path = os.path.join(GIF_DIRECTORY, filename)
#         thumbnail_path = os.path.join(THUMBNAIL_DIRECTORY, thumbnail_filename)
        
#         # base64 GIF 데이터가 있으면 저장
#         if 'base64_data' in data:
#             if not save_base64_to_file(data['base64_data'], gif_path):
#                 return jsonify({
#                     'success': False,
#                     'error': 'GIF 파일 저장 실패'
#                 }), 500
#             if not save_base64_to_file(data['base64_data'], thumbnail_path):
#                 return jsonify({
#                     'success': False,
#                     'error': 'GIF 파일 저장 실패'
#                 }), 500
            
        
#         # # base64 썸네일 데이터가 있으면 저장
#         # if 'thumbnail_base64_data' in data:
#         #     if not save_base64_to_file(data['thumbnail_base64_data'], thumbnail_path):
#         #         # 썸네일 저장 실패 시 원본 GIF를 썸네일로 사용
#         #         thumbnail_path = gif_path
#         # elif 'base64_data' in data:
#         #     # 썸네일이 없으면 원본 GIF를 썸네일로 사용
#         #     thumbnail_path = gif_path
        
#         # LocalGif 객체 생성
#         new_gif = {
#             'id': gif_id,
#             'title': data['title'],
#             'url': f'/gifs/{filename}' if 'base64_data' in data else data.get('url', ''),
#             'thumbnailUrl': f'/gifs/thumbnails/{os.path.basename(thumbnail_path)}' if 'base64_data' in data else data.get('thumbnailUrl', ''),
#             'tags': data['tags']
#         }
        
#         # 기존 GIF 목록에 추가
#         gifs = load_gifs()
#         gifs.append(new_gif)
        
#         # 저장
#         if save_gifs(gifs):
#             return jsonify({
#                 'success': True,
#                 'message': 'GIF가 성공적으로 추가되었습니다.',
#                 'data': new_gif
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'error': 'GIF 목록 저장 실패'
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/gifs/<gif_id>', methods=['DELETE'])
# def delete_gif(gif_id: str):
#     """GIF 삭제"""
#     try:
#         gifs = load_gifs()
        
#         # 삭제할 GIF 찾기
#         gif_to_delete = None
#         for gif in gifs:
#             if gif['id'] == gif_id:
#                 gif_to_delete = gif
#                 break
        
#         if not gif_to_delete:
#             return jsonify({
#                 'success': False,
#                 'error': 'GIF를 찾을 수 없습니다.'
#             }), 404
        
#         # 파일 삭제 시도
#         try:
#             if gif_to_delete['url'].startswith('/gifs/'):
#                 file_path = gif_to_delete['url'].replace('/gifs/', f'{GIF_DIRECTORY}/')
#                 if os.path.exists(file_path):
#                     os.remove(file_path)
            
#             if gif_to_delete['thumbnailUrl'].startswith('/gifs/thumbnails/'):
#                 thumbnail_path = gif_to_delete['thumbnailUrl'].replace('/gifs/thumbnails/', f'{THUMBNAIL_DIRECTORY}/')
#                 if os.path.exists(thumbnail_path):
#                     os.remove(thumbnail_path)
#         except Exception as e:
#             print(f"파일 삭제 중 오류 (무시됨): {e}")
        
#         # 목록에서 제거
#         gifs = [gif for gif in gifs if gif['id'] != gif_id]
        
#         # 저장
#         if save_gifs(gifs):
#             return jsonify({
#                 'success': True,
#                 'message': 'GIF가 성공적으로 삭제되었습니다.',
#                 'deleted_gif': gif_to_delete
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'error': 'GIF 목록 저장 실패'
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/gifs/search', methods=['GET'])
# def search_gifs():
#     """태그로 GIF 검색"""
#     try:
#         query = request.args.get('q', '').lower()
#         gifs = load_gifs()
        
#         if not query:
#             return jsonify({
#                 'success': True,
#                 'data': gifs,
#                 'count': len(gifs)
#             })
        
#         # 제목이나 태그에서 검색
#         filtered_gifs = []
#         for gif in gifs:
#             if (query in gif['title'].lower() or 
#                 any(query in tag.lower() for tag in gif['tags'])):
#                 filtered_gifs.append(gif)
        
#         return jsonify({
#             'success': True,
#             'data': filtered_gifs,
#             'count': len(filtered_gifs),
#             'query': query
#         })
        
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# @app.route('/health', methods=['GET'])
# def health_check():
#     """헬스 체크"""
#     return jsonify({
#         'success': True,
#         'message': 'GIF 관리 서버가 정상적으로 동작 중입니다.',
#         'timestamp': datetime.now().isoformat()
#     })

# if __name__ == '__main__':
#     print("🎬 GIF 관리 서버 시작...")
#     print("📁 GIF 디렉토리:", GIF_DIRECTORY)
#     print("📄 JSON 파일:", JSON_FILE_PATH)
#     print("🌐 서버 주소: http://localhost:5000")
#     print("\n사용 가능한 엔드포인트:")
#     print("  GET    /gifs           - GIF 목록 조회")
#     print("  POST   /gifs           - GIF 추가")
#     print("  DELETE /gifs/<id>      - GIF 삭제")
#     print("  GET    /gifs/search    - GIF 검색")
#     print("  GET    /health         - 헬스 체크")
    
#     app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import base64
import os
from typing import List, Dict, Any
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)  # CORS 설정 (프론트엔드와 연결을 위해)

# 설정
JSON_FILE_PATH = 'users_gifs.json'
GIF_DIRECTORY = '/opt/mattermost/client/gifs'
THUMBNAIL_DIRECTORY = '/opt/mattermost/client/gifs/thumbnails'

# 디렉토리 생성
os.makedirs(GIF_DIRECTORY, exist_ok=True)
os.makedirs(THUMBNAIL_DIRECTORY, exist_ok=True)

# LocalGif 타입 정의
class LocalGif:
    def __init__(self, id: str, title: str, url: str, thumbnailUrl: str, tags: List[str], userId: str):
        self.id = id
        self.title = title
        self.url = url
        self.thumbnailUrl = thumbnailUrl
        self.tags = tags
        self.userId = userId
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'thumbnailUrl': self.thumbnailUrl,
            'tags': self.tags,
            'userId': self.userId
        }

# 기본 GIF 데이터 (각 사용자마다 초기화됨)
DEFAULT_LOCAL_GIFS = []

def load_users_gifs() -> Dict[str, List[Dict[str, Any]]]:
    """JSON 파일에서 사용자별 GIF 목록을 로드"""
    try:
        if os.path.exists(JSON_FILE_PATH):
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 파일이 없으면 빈 딕셔너리로 초기화
            save_users_gifs({})
            return {}
    except Exception as e:
        print(f"사용자 GIF 로드 중 오류: {e}")
        return {}

def save_users_gifs(users_gifs: Dict[str, List[Dict[str, Any]]]) -> bool:
    """사용자별 GIF 목록을 JSON 파일에 저장"""
    try:
        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(users_gifs, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"사용자 GIF 저장 중 오류: {e}")
        return False

def get_user_gifs(user_id: str) -> List[Dict[str, Any]]:
    """특정 사용자의 GIF 목록 반환"""
    users_gifs = load_users_gifs()
    if user_id not in users_gifs:
        # 새 사용자면 기본 GIF로 초기화
        users_gifs[user_id] = [
            {**gif, 'userId': user_id} for gif in DEFAULT_LOCAL_GIFS
        ]
        save_users_gifs(users_gifs)
    return users_gifs[user_id]

def save_user_gifs(user_id: str, gifs: List[Dict[str, Any]]) -> bool:
    """특정 사용자의 GIF 목록 저장"""
    users_gifs = load_users_gifs()
    users_gifs[user_id] = gifs
    return save_users_gifs(users_gifs)

def save_base64_to_file(base64_data: str, filename: str) -> bool:
    """base64 데이터를 파일로 저장"""
    try:
        # base64 헤더 제거 (data:image/gif;base64, 부분)
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
        
        # base64 디코딩
        gif_data = base64.b64decode(base64_data)
        
        # 파일 저장
        with open(filename, 'wb') as f:
            f.write(gif_data)
        
        return True
    except Exception as e:
        print(f"파일 저장 중 오류: {e}")
        return False

def get_user_id_from_request() -> str:
    """요청에서 사용자 ID 추출"""
    # 쿼리 파라미터에서 확인
    user_id = request.args.get('userId')
    if user_id:
        return user_id
    
    # POST 요청의 경우 body에서 확인
    if request.method == 'POST' and request.json:
        user_id = request.json.get('userId')
        if user_id:
            return user_id
    
    # Authorization 헤더에서 확인 (Bearer 토큰 방식)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        # 실제 환경에서는 토큰을 검증하여 사용자 ID를 추출해야 함
        return auth_header.replace('Bearer ', '')
    
    # 기본값 또는 에러 처리
    return None

@app.route('/gifs', methods=['GET'])
def get_gifs():
    """사용자별 GIF 목록 반환"""
    try:
        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': '사용자 ID가 필요합니다.'
            }), 400
        
        gifs = get_user_gifs(user_id)
        return jsonify({
            'success': True,
            'data': gifs,
            'count': len(gifs),
            'userId': user_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/gifs', methods=['POST'])
def add_gif():
    """사용자별 새 GIF 추가"""
    try:
        data = request.json
        
        # 사용자 ID 확인 (쿼리 파라미터 또는 body에서)
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({
                'success': False,
                'error': '사용자 ID가 필요합니다.'
            }), 400
        
        # 필수 필드 확인
        required_fields = ['title', 'tags']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'필수 필드 누락: {field}'
                }), 400
        
        # 고유 ID 생성
        gif_id = data.get('id', str(uuid.uuid4()))
        
        # 파일명 생성 (사용자별 디렉토리)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{user_id}_{gif_id}_{timestamp}.gif"
        thumbnail_filename = f"{user_id}_{gif_id}_{timestamp}_thumb.gif"
        
        gif_path = os.path.join(GIF_DIRECTORY, filename)
        thumbnail_path = os.path.join(THUMBNAIL_DIRECTORY, thumbnail_filename)
        
        # base64 GIF 데이터가 있으면 저장
        if 'base64_data' in data:
            if not save_base64_to_file(data['base64_data'], gif_path):
                return jsonify({
                    'success': False,
                    'error': 'GIF 파일 저장 실패'
                }), 500
            if not save_base64_to_file(data['base64_data'], thumbnail_path):
                return jsonify({
                    'success': False,
                    'error': 'GIF 썸네일 저장 실패'
                }), 500
        
        # LocalGif 객체 생성
        new_gif = {
            'id': gif_id,
            'title': data['title'],
            'url': f'/static/gifs/{filename}' if 'base64_data' in data else data.get('url', ''),
            'thumbnailUrl': f'/static/gifs/thumbnails/{thumbnail_filename}' if 'base64_data' in data else data.get('thumbnailUrl', ''),
            'tags': data['tags'],
            'userId': user_id
        }
        
        # 사용자의 기존 GIF 목록에 추가
        user_gifs = get_user_gifs(user_id)
        user_gifs.append(new_gif)
        
        # 저장
        if save_user_gifs(user_id, user_gifs):
            return jsonify({
                'success': True,
                'message': 'GIF가 성공적으로 추가되었습니다.',
                'data': new_gif
            })
        else:
            return jsonify({
                'success': False,
                'error': 'GIF 목록 저장 실패'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/gifs/<gif_id>', methods=['DELETE'])
def delete_gif(gif_id: str):
    """사용자별 GIF 삭제"""
    try:
        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': '사용자 ID가 필요합니다.'
            }), 400
        
        user_gifs = get_user_gifs(user_id)
        
        # 삭제할 GIF 찾기 (해당 사용자의 GIF만)
        gif_to_delete = None
        for gif in user_gifs:
            if gif['id'] == gif_id and gif['userId'] == user_id:
                gif_to_delete = gif
                break
        
        if not gif_to_delete:
            return jsonify({
                'success': False,
                'error': 'GIF를 찾을 수 없거나 삭제 권한이 없습니다.'
            }), 404
        
        # 파일 삭제 시도
        try:
            if gif_to_delete['url'].startswith('/gifs/'):
                file_path = gif_to_delete['url'].replace('/gifs/', f'{GIF_DIRECTORY}/')
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            if gif_to_delete['thumbnailUrl'].startswith('/gifs/thumbnails/'):
                thumbnail_path = gif_to_delete['thumbnailUrl'].replace('/gifs/thumbnails/', f'{THUMBNAIL_DIRECTORY}/')
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
        except Exception as e:
            print(f"파일 삭제 중 오류 (무시됨): {e}")
        
        # 사용자 목록에서 제거
        user_gifs = [gif for gif in user_gifs if gif['id'] != gif_id]
        
        # 저장
        if save_user_gifs(user_id, user_gifs):
            return jsonify({
                'success': True,
                'message': 'GIF가 성공적으로 삭제되었습니다.',
                'deleted_gif': gif_to_delete
            })
        else:
            return jsonify({
                'success': False,
                'error': 'GIF 목록 저장 실패'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/gifs/search', methods=['GET'])
def search_gifs():
    """사용자별 태그로 GIF 검색"""
    try:
        user_id = get_user_id_from_request()
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': '사용자 ID가 필요합니다.'
            }), 400
        
        query = request.args.get('q', '').lower()
        user_gifs = get_user_gifs(user_id)
        
        if not query:
            return jsonify({
                'success': True,
                'data': user_gifs,
                'count': len(user_gifs),
                'userId': user_id
            })
        
        # 제목이나 태그에서 검색
        filtered_gifs = []
        for gif in user_gifs:
            if (query in gif['title'].lower() or 
                any(query in tag.lower() for tag in gif['tags'])):
                filtered_gifs.append(gif)
        
        return jsonify({
            'success': True,
            'data': filtered_gifs,
            'count': len(filtered_gifs),
            'query': query,
            'userId': user_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/users/<user_id>/gifs', methods=['GET'])
def get_user_gifs_by_path(user_id: str):
    """경로로 사용자별 GIF 목록 반환"""
    try:
        gifs = get_user_gifs(user_id)
        return jsonify({
            'success': True,
            'data': gifs,
            'count': len(gifs),
            'userId': user_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/users/<user_id>/gifs', methods=['POST'])
def add_user_gif_by_path(user_id: str):
    """경로로 사용자별 새 GIF 추가"""
    try:
        data = request.json
        
        # 필수 필드 확인
        required_fields = ['title', 'tags']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'필수 필드 누락: {field}'
                }), 400
        
        # URL 경로의 user_id 사용
        data['userId'] = user_id
        
        # 기존 add_gif 로직 재사용
        return add_gif()
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/users/<user_id>/gifs/<gif_id>', methods=['DELETE'])
def delete_user_gif_by_path(user_id: str, gif_id: str):
    """경로로 사용자별 GIF 삭제"""
    try:
        user_gifs = get_user_gifs(user_id)
        
        # 삭제할 GIF 찾기 (해당 사용자의 GIF만)
        gif_to_delete = None
        for gif in user_gifs:
            if gif['id'] == gif_id and gif['userId'] == user_id:
                gif_to_delete = gif
                break
        
        if not gif_to_delete:
            return jsonify({
                'success': False,
                'error': 'GIF를 찾을 수 없습니다.'
            }), 404
        
        # 파일 삭제 시도
        try:
            if gif_to_delete['url'].startswith('/gifs/'):
                file_path = gif_to_delete['url'].replace('/gifs/', f'{GIF_DIRECTORY}/')
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            if gif_to_delete['thumbnailUrl'].startswith('/gifs/thumbnails/'):
                thumbnail_path = gif_to_delete['thumbnailUrl'].replace('/gifs/thumbnails/', f'{THUMBNAIL_DIRECTORY}/')
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
        except Exception as e:
            print(f"파일 삭제 중 오류 (무시됨): {e}")
        
        # 사용자 목록에서 제거
        user_gifs = [gif for gif in user_gifs if gif['id'] != gif_id]
        
        # 저장
        if save_user_gifs(user_id, user_gifs):
            return jsonify({
                'success': True,
                'message': 'GIF가 성공적으로 삭제되었습니다.',
                'deleted_gif': gif_to_delete
            })
        else:
            return jsonify({
                'success': False,
                'error': 'GIF 목록 저장 실패'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/users/<user_id>/gifs/search', methods=['GET'])
def search_user_gifs_by_path(user_id: str):
    """경로로 사용자별 태그로 GIF 검색"""
    try:
        query = request.args.get('q', '').lower()
        user_gifs = get_user_gifs(user_id)
        
        if not query:
            return jsonify({
                'success': True,
                'data': user_gifs,
                'count': len(user_gifs),
                'userId': user_id
            })
        
        # 제목이나 태그에서 검색
        filtered_gifs = []
        for gif in user_gifs:
            if (query in gif['title'].lower() or 
                any(query in tag.lower() for tag in gif['tags'])):
                filtered_gifs.append(gif)
        
        return jsonify({
            'success': True,
            'data': filtered_gifs,
            'count': len(filtered_gifs),
            'query': query,
            'userId': user_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'success': True,
        'message': '사용자별 GIF 관리 서버가 정상적으로 동작 중입니다.',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🎬 사용자별 GIF 관리 서버 시작...")
    print("📁 GIF 디렉토리:", GIF_DIRECTORY)
    print("📄 JSON 파일:", JSON_FILE_PATH)
    print("🌐 서버 주소: http://chlee.postech.ac.kr:5000")
    print("\n사용 가능한 엔드포인트:")
    print("  GET    /gifs?userId=<id>              - 사용자별 GIF 목록 조회")
    print("  POST   /gifs                          - 사용자별 GIF 추가 (userId 필요)")
    print("  DELETE /gifs/<id>?userId=<id>         - 사용자별 GIF 삭제")
    print("  GET    /gifs/search?q=<query>&userId=<id> - 사용자별 GIF 검색")
    print("  GET    /users/<userId>/gifs           - 특정 사용자 GIF 목록")
    print("  POST   /users/<userId>/gifs           - 특정 사용자 GIF 추가")
    print("  DELETE /users/<userId>/gifs/<id>      - 특정 사용자 GIF 삭제")
    print("  GET    /users/<userId>/gifs/search    - 특정 사용자 GIF 검색")
    print("  GET    /health                        - 헬스 체크")
    
    app.run(debug=True, host='0.0.0.0', port=5000)