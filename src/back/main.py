from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5500", "http://127.0.0.1:5500"]}})

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
USERS_FILE = os.path.join(DATA_FOLDER, "users.json")
COUNTER_FILE = os.path.join(DATA_FOLDER, "vCount.json")

def get_next_v_hex_id():
    try:
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            counter_data = json.load(f)
        total_videos = counter_data["totalVideos"]
        
        total_videos += 1
        
        hex_id = hex(total_videos-1)[2:]
        
        with open(COUNTER_FILE, "w", encoding="utf-8") as f:
            json.dump({"totalVideos": total_videos}, f, indent=2)
        
        return hex_id
    except FileNotFoundError:
        with open(COUNTER_FILE, "w", encoding="utf-8") as f:
            json.dump({"totalVideos": 1}, f, indent=2)
        return "1"
    except Exception as e:
        print(f"获取视频 ID 失败：{e}")
        return None

@app.route("/api/users", methods=["GET"])
def get_all_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        return jsonify(users_data)
    except FileNotFoundError:
        return jsonify({"error": "cannot find users.json"}), 404
    except Exception as e:
        return jsonify({"error": f"invalid data: {str(e)}"}), 500

@app.route("/api/videos/add", methods=["POST"])
def add_new_video():
    try:
        request_data = request.get_json()
        user_id = request_data.get("userId")
        video_title = request_data.get("title")
        video_src = request_data.get("src")
        video_picture = request_data.get("picture")
        
        if not all([user_id, video_title, video_src]):
            return jsonify({"error": "missing parameters! userId, title, src must be provided"}), 400
        
        hex_vid = get_next_v_hex_id()
        if not hex_vid:
            return jsonify({"error": "failed to generate vid"}), 500
        
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        
        if user_id not in users_data:
            return jsonify({"error": "cannot find user"}), 404
        
        users_data[user_id]["Videos"].append({
            "Title": video_title,
            "Vid": hex_vid,
            "Src": video_src,
            "Picture": video_picture
        })
        
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            total = json.load(f)["totalVideos"]
        return jsonify({
            "success": True,
            "vid": hex_vid,
            "totalVideos": total
        })
    
    except Exception as e:
        print(f"添加视频失败：{e}")
        return jsonify({"error": "cannot add video"}), 500
@app.route("/api/videos/delete", methods=["GET"])
def delete_video():
    try:
        vid = request.args.get("vid")
        if not vid:
            return jsonify({"error": "missing parameter! vid must be provided"}), 400
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        
        for user_id in users_data:
            for video in users_data[user_id]["Videos"]:
                if video["Vid"] == vid:
                    users_data[user_id]["Videos"].remove(video)
                    break
        
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            total = json.load(f)["totalVideos"]
        return jsonify({
            "success": True,
            "vid": vid,
            "totalVideos": total
        })
    
    except Exception as e:
        print(f"删除视频失败：{e}")
        return jsonify({"error": "cannot delete video"}), 500

@app.route("/api/videos/get", methods=["GET"])
def get_video_by_id():
    try:
        vid = request.args.get("vid")
        if not vid:
            return jsonify({"error": "missing parameter! vid must be provided"}), 400
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        
        for user_id, user_info in users_data.items():
            for video in users_data[user_id]["Videos"]:
                if video["Vid"] == vid:
                    return jsonify({
                        **video,
                        "Maker": user_info
                    })
        
        return jsonify({"error": "cannot find video"}), 404
    except Exception as e:
        print(f"获取视频失败：{e}")
        return jsonify({"error": "cannot get video"}), 500

@app.route("/api/videos/get/all", methods=["GET"])
def get_all_videos():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        
        all_videos = []
        for user_id, user_info in users_data.items():
             for video in user_info["Videos"]:
                all_videos.append({
                    **video,
                    "Maker": user_info
                })
        
        return jsonify(all_videos)
    except Exception as e:
        print(f"获取所有视频失败：{e}")
        return jsonify({"error": "cannot get all videos"}), 500
@app.route("/api/videos/get/random", methods=["GET"])
def get_random_fifty_videos():
    try:
        import random
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        
        all_videos = []
        for user_id, user_info in users_data.items():
             for video in user_info["Videos"]:
                all_videos.append({
                    **video,
                    "Maker": user_info
                })
        
        random_videos = random.sample(all_videos, min(50, len(all_videos)))
        
        return jsonify(random_videos)
    except Exception as e:
        print(f"获取随机视频失败：{e}")
        return jsonify({"error": "cannot get random videos"}), 500

if __name__ == "__main__":
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    app.run(host="0.0.0.0", port=3000, debug=True)