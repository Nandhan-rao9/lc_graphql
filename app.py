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
    if data is None:
        return jsonify({
            "error": "Connection Error", 
            "message": "Could not reach LeetCode API. Check your internet or if LeetCode is down."
        }), 503

    if "errors" in data:
        return jsonify({
            "error": "LeetCode GraphQL Error", 
            "details": data.get("errors")
        }), 400
    
    result = data
    for key in key_path:
        result = result.get(key) 
        if result is None:
            return jsonify({"error": "Resource not found on LeetCode"}), 404
            
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

@app.route('/<username>/contests', methods=['GET'])
def get_contests(username):
    data = make_leetcode_request(q.USER_CONTEST_QUERY, {"username": username})
    return handle_response(data, ["data", "userContestRanking"])

@app.route('/problems', methods=['GET'])
def get_problems():
    category_slug = request.args.get('categorySlug', default="", type=str)
    limit = request.args.get('limit', default=50, type=int)
    skip = request.args.get('skip', default=0, type=int)
    
    variables = {
        "categorySlug": category_slug, 
        "limit": limit, 
        "skip": skip, 
        "filters": {} 
    }
    
    data = make_leetcode_request(q.GET_PROBLEMS_QUERY, variables)
    
    return handle_response(data, ["data", "problemsetQuestionList"])


if __name__ == "__main__":
    app.run(port=Config.PORT, debug=Config.DEBUG)