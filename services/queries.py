# 1. Basic User Profile & Stats
USER_PROFILE_QUERY = """
query userPublicProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      ranking
      userAvatar
      realName
      aboutMe
      school
      websites
      countryName
      reputation
    }
  }
}
"""

# 2. Earned & Upcoming Badges
USER_BADGES_QUERY = """
query userBadges($username: String!) {
  matchedUser(username: $username) {
    badges {
      id
      name
      shortName
      icon
    }
    upcomingBadges {
      name
      icon
    }
  }
}
"""

# 3. Submission Calendar (Heatmap)
USER_CALENDAR_QUERY = """
query userSearchCalendar($username: String!, $year: Int) {
  matchedUser(username: $username) {
    userCalendar(year: $year) {     
       activeYears      
       streak      
       totalActiveDays      
       dccBadges {        
       timestamp        
       badge {          
       name          
       icon        
       }      
       }      
       submissionCalendar    
    }
  }
}
"""

# 4. Recent Submissions (Public)
USER_SUBMISSIONS_QUERY = """
query userRecentSubmissions($username: String!, $limit: Int!) {
  recentSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
    timestamp
    statusDisplay
    lang
  }
}
"""
