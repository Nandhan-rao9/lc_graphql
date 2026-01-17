from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from services.leetcode_client import make_leetcode_request
import services.queries as q
import json

app = Flask(__name__)
CORS(app)

# Helper to handle errors
def handle_response(data, key_path):
    if not data or "errors" in data:
        return jsonify({"error": "LeetCode API Error", "details": data.get("errors")}), 500
    
    # Traverse the nested dictionary (e.g., ["data", "matchedUser"])
    result = data
    for key in key_path:
        result = result.get(key, {})
        if result is None:
            return jsonify({"error": "Not Found"}), 404
            
    return jsonify(result)

@app.route('/<username>', methods=['GET'])
def get_profile(username):
    data = make_leetcode_request(q.USER_PROFILE_QUERY, {"username": username})
    return handle_response(data, ["data", "matchedUser"])

@app.route('/<username>/badges', methods=['GET'])
def get_badges(username):
    data = make_leetcode_request(q.USER_BADGES_QUERY, {"username": username})
    return handle_response(data, ["data", "matchedUser", "badges"])


@app.route('/<username>/calendar', methods=['GET'])
def get_calendar(username):
    data = make_leetcode_request(q.USER_CALENDAR_QUERY, {"username": username})
    res = handle_response(data, ["data", "matchedUser", "userCalendar"])
    
    # Parse the stringified JSON calendar if success
    if res.status_code == 200:
        content = res.get_json()
        content["submissionCalendar"] = json.loads(content["submissionCalendar"])
        return jsonify(content)
    return res

@app.route('/<username>/submissions', methods=['GET'])
def get_submissions(username):
    limit = request.args.get('limit', default=20, type=int)
    data = make_leetcode_request(q.USER_SUBMISSIONS_QUERY, {"username": username, "limit": limit})
    return handle_response(data, ["data", "recentSubmissionList"])

if __name__ == "__main__":
    app.run(port=Config.PORT, debug=Config.DEBUG)