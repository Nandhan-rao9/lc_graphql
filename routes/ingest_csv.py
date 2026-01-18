import os
import csv
from urllib.parse import urlparse
from flask import Blueprint, jsonify
from utils.db import db

csv_ingest_bp = Blueprint("csv_ingest", __name__)
problems_col = db["problems_master"]

CSV_DIR = "companies_csv"


def extract_slug(problem_link: str) -> str | None:
    """
    Extracts titleSlug from a LeetCode problem URL.
    """
    try:
        path = urlparse(problem_link).path
        parts = path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "problems":
            return parts[1]
    except Exception:
        pass
    return None


@csv_ingest_bp.route("/api/ingest/companies", methods=["POST"])
def ingest_company_csvs():
    if not os.path.isdir(CSV_DIR):
        return jsonify({"error": f"{CSV_DIR} folder not found"}), 400

    total_updates = 0
    skipped = 0

    for filename in os.listdir(CSV_DIR):
        if not filename.lower().endswith(".csv"):
            continue

        company = filename.replace(".csv", "").strip()
        filepath = os.path.join(CSV_DIR, filename)

        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                slug = extract_slug(row.get("problem_link", ""))
                if not slug:
                    skipped += 1
                    continue

                try:
                    freq = int(row.get("num_occur", 1))
                except ValueError:
                    freq = 1

                result = problems_col.update_one(
                    {"_id": slug},
                    {
                        "$addToSet": {"companies": company},
                        "$inc": {
                            f"by_company.{company}": freq,
                            "num_occur": freq
                        }
                    }
                )

                if result.matched_count == 0:
                    skipped += 1
                else:
                    total_updates += 1

    return jsonify({
        "status": "success",
        "updated": total_updates,
        "skipped": skipped
    })
