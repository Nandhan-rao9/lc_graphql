import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PORT=int(os.getenv("PORT", 9009))
    DEBUG=os.getenv("DEBUG", "True") == "True"
    LEETCODE_URL="https://leetcode.com/graphql"