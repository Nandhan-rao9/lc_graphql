# Query for basic user profile information
USER_PROFILE_QUERY = """
query userPublicProfile($username: String!) {
  matchedUser(username: $username) {
    username
    githubUrl
    twitterUrl
    linkedinUrl
    profile {
      realName
      aboutMe
      school
      websites
      countryName
      userAvatar
      reputation
      ranking
    }
  }
}
"""

