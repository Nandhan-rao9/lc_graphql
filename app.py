from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

from config import Config
from routes.ingest_csv import csv_ingest_bp
from services.leetcode_client import LeetCodeClient
import services.queries as q
from routes.ingest import ingest_bp
from routes.ingest_user import user_ingest_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

# Create ONE client instance
leetcode_client = LeetCodeClient()
app.config["LEETCODE_CLIENT"] = leetcode_client

app.register_blueprint(ingest_bp)
app.register_blueprint(csv_ingest_bp)
app.register_blueprint(user_ingest_bp)

# -------------------- Helpers --------------------


def handle_response(data, key_path):
    if data is None:
        return jsonify({
            "error": "Connection Error",
            "message": "Failed to reach LeetCode"
        }), 503

    if "errors" in data:
        return jsonify({
            "error": "LeetCode GraphQL Error",
            "details": data["errors"]
        }), 400

    result = data
    for key in key_path:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return jsonify({"error": "Unexpected response format"}), 500

        if result is None:
            return jsonify({"error": "Resource not found"}), 404

    return jsonify(result), 200

# -------------------- Routes --------------------

@app.route("/<username>", methods=["GET"])
def get_profile(username):
    data = leetcode_client.fetch(
        q.USER_PROFILE_QUERY,
        {"username": username}
    )
    return handle_response(data, ["data", "matchedUser"])


@app.route("/<username>/badges", methods=["GET"])
def get_badges(username):
    data = leetcode_client.fetch(
        q.USER_BADGES_QUERY,
        {"username": username}
    )
    return handle_response(data, ["data", "matchedUser", "badges"])


@app.route("/<username>/calendar", methods=["GET"])
def get_calendar(username):
    data = leetcode_client.fetch(
        q.USER_CALENDAR_QUERY,
        {"username": username}
    )

    res, status = handle_response(
        data,
        ["data", "matchedUser", "userCalendar"]
    )

    if status == 200:
        content = res.get_json()
        calendar = content.get("submissionCalendar")
        if isinstance(calendar, str):
            content["submissionCalendar"] = json.loads(calendar)
        return jsonify(content)

    return res, status


@app.route("/<username>/submissions", methods=["GET"])
def get_submissions(username):
    limit = request.args.get("limit", 20, type=int)
    data = leetcode_client.fetch(
        q.USER_SUBMISSIONS_QUERY,
        {"username": username, "limit": limit}
    )
    return handle_response(data, ["data", "recentSubmissionList"])


@app.route("/<username>/contests", methods=["GET"])
def get_contests(username):
    data = leetcode_client.fetch(
        q.USER_CONTEST_QUERY,
        {"username": username}
    )
    return handle_response(data, ["data", "userContestRanking"])


@app.route("/problems", methods=["GET"])
def get_problems():
    variables = {
        "categorySlug": request.args.get("categorySlug", ""),
        "limit": request.args.get("limit", 50, type=int),
        "skip": request.args.get("skip", 0, type=int),
        "filters": {}
    }

    data = leetcode_client.fetch(q.GET_PROBLEMS_QUERY, variables)
    return handle_response(data, ["data", "problemsetQuestionList"])


@app.route("/daily", methods=["GET"])
def get_daily():
    data = leetcode_client.fetch(q.DAILY_QUESTION_QUERY)
    return handle_response(
        data,
        ["data", "activeDailyCodingChallengeQuestion"]
    )


@app.route("/<username>/ac-submissions", methods=["GET"])
def get_user_ac_submissions(username):
    limit = request.args.get("limit", 20, type=int)
    data = leetcode_client.fetch(
        q.USER_AC_SUBMISSIONS_QUERY,
        {"username": username, "limit": limit}
    )
    return handle_response(data, ["data", "recentAcSubmissionList"])


# -------------------- Sync Example --------------------

@app.route("/sync/full-history", methods=["POST"])
def sync_full_history():
    offset = 0
    limit = 20
    total_synced = 0
    has_next = True

    while has_next and total_synced < 500:
        data = leetcode_client.fetch(
            q.FULL_SUBMISSION_LIST_QUERY,
            {"offset": offset, "limit": limit}
        )

        if not data or "data" not in data:
            break

        submission_data = data["data"]["submissionList"]
        has_next = submission_data["hasNext"]
        submissions = submission_data["submissions"]

        for sub in submissions:
            if sub["statusDisplay"] == "Accepted":
                solve_date = datetime.fromtimestamp(int(sub["timestamp"]))
                next_rev = solve_date + timedelta(days=7)

                # db.submissions.update_one(...)

                total_synced += 1

        offset += limit

    return jsonify({
        "status": "success",
        "total_synced": total_synced
    })


if __name__ == "__main__":
    app.run(
        port=Config.PORT,
        debug=Config.DEBUG
    )
