# import requests
#
# def get_reddit_titles():
#     HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
#     url = f"https://www.reddit.com/r/{input('enter subreddit name')}/hot.json?limit=50"
#     res = requests.get(url, headers=HEADERS)
#     data = res.json()
#     children = data["data"]["children"]
#
#     clean_title=[]
#     for post in children:
#         title = post["data"]["title"]
#         y = title.replace("\n", " ").strip()
#         clean_title.append(y)
#     return clean_title
#
# # print(get_reddit_titles())
# class RedditScraper:
#     def __init__(self):
#         # User-Agent is required to avoid 429 errors from Reddit
#         self.headers = {'User-Agent': 'Mozilla/5.0 (MyRedditApp/1.0)'}
#
#     def fetch_data(self, mode, query_term):
#         """
#         Fetches JSON data from Reddit based on the user's selected mode.
#         Returns a list of dicts: [{'link': '...', 'text': '...'}]
#         """
#         url = ""
#         limit="25"
#         if mode == "1":  # Subreddit
#             print(f"🕵️  Fetching hot posts from r/{query_term}...")
#             url = f"https://www.reddit.com/r/{query_term}/hot.json?limit={limit}"
#         elif mode == "2":  # Topic
#             print(f"🕵️  Searching Reddit for topic: '{query_term}'...")
#             url = f"https://www.reddit.com/search.json?q={query_term}&limit={limit}"
#         elif mode == "3":  # User
#             print(f"🕵️  Fetching comments from u/{query_term}...")
#             url = f"https://www.reddit.com/user/{query_term}/comments/.json?limit={limit}"
#
#         try:
#             response = requests.get(url, headers=self.headers)
#             if response.status_code != 200:
#                 print(f"❌ Error: Reddit returned status {response.status_code}")
#                 return []
#
#             data = response.json()
#             raw_posts = []
#
#             for item in data['data']['children']:
#                 d = item['data']
#
#                 # 1. Construct Link
#                 permalink = d.get('permalink', '')
#                 full_link = f"https://www.reddit.com{permalink}"
#
#                 # 2. Construct Text (Title + Body)
#                 title = d.get('title', '')
#                 body = d.get('selftext', '') or d.get('body', '')  # 'selftext' for posts, 'body' for comments
#                 full_text = f"{title} {body}".strip()
#
#                 if full_text:
#                     raw_posts.append({'link': full_link, 'text': full_text})
#
#             print(f"✅ Successfully fetched {len(raw_posts)} items.")
#             return raw_posts,data
#
#         except Exception as e:
#             print(f"❌ Network Error: {e}")
#             return [],{}


"""
Reddit Pulse - Reddit Data Scraper Module
==========================================
This module handles fetching data from Reddit's public JSON API without
requiring authentication or API keys.

Supported Modes:
    1. Subreddit: Fetch hot posts from a specific subreddit
    2. Topic: Search Reddit for posts matching a keyword
    3. User: Fetch comments from a specific user's profile

Author: Reddit Pulse Team
License: MIT
"""

import requests


class RedditScraper:
    """
    Lightweight Reddit scraper using public JSON endpoints.

    This scraper fetches data from Reddit without authentication by
    appending .json to Reddit URLs and parsing the response.
    """

    def __init__(self):
        """
        Initialize the scraper with required headers.

        Note:
            User-Agent header is required to avoid 429 (Too Many Requests) errors
            from Reddit's rate limiting system.
        """
        self.headers = {'User-Agent': 'Mozilla/5.0 (MyRedditApp/1.0)'}

    def fetch_data(self, mode, query_term):
        """
        Fetch Reddit data based on the selected mode and query.

        Args:
            mode (str): Search mode
                - '1': Subreddit (e.g., 'python', 'AskReddit')
                - '2': Topic/Keyword (e.g., 'machine learning')
                - '3': User (e.g., 'spez')
            query_term (str): The search query or identifier

        Returns:
            tuple: (scraped_posts, raw_json_data)
                - scraped_posts (list[dict]): Cleaned posts with 'link' and 'text' keys
                - raw_json_data (dict): Full JSON response from Reddit API

        Example:
            scraper = RedditScraper()
            posts, raw = scraper.fetch_data('1', 'python')
            # posts = [{'link': 'https://...', 'text': 'Title and body...'}, ...]
        """
        url = ""
        limit = "25"  # Number of posts to fetch

        # Build URL based on mode
        if mode == "1":  # Subreddit mode
            print(f"🕵️  Fetching hot posts from r/{query_term}...")
            url = f"https://www.reddit.com/r/{query_term}/hot.json?limit={limit}"

        elif mode == "2":  # Topic search mode
            print(f"🕵️  Searching Reddit for topic: '{query_term}'...")
            url = f"https://www.reddit.com/search.json?q={query_term}&limit={limit}"

        elif mode == "3":  # User profile mode
            print(f"🕵️  Fetching comments from u/{query_term}...")
            url = f"https://www.reddit.com/user/{query_term}/comments/.json?limit={limit}"

        try:
            # Make HTTP request to Reddit
            response = requests.get(url, headers=self.headers)

            # Check for errors
            if response.status_code != 200:
                print(f"❌ Error: Reddit returned status {response.status_code}")
                return [], {}

            # Parse JSON response
            data = response.json()
            raw_posts = []

            # Extract relevant data from each post/comment
            for item in data['data']['children']:
                d = item['data']

                # Build full Reddit URL
                permalink = d.get('permalink', '')
                full_link = f"https://www.reddit.com{permalink}"

                # Combine title and body for comprehensive analysis
                # Posts have 'title' and 'selftext'
                # Comments have 'body'
                title = d.get('title', '')
                body = d.get('selftext', '') or d.get('body', '')
                full_text = f"{title} {body}".strip()

                # Only include items with actual text content
                if full_text:
                    raw_posts.append({
                        'link': full_link,
                        'text': full_text
                    })

            print(f"✅ Successfully fetched {len(raw_posts)} items.")
            return raw_posts, data

        except Exception as e:
            print(f"❌ Network Error: {e}")
            return [], {}


# ============================================================================
# LEGACY FUNCTION (For backward compatibility)
# ============================================================================

def get_reddit_titles():
    """
    Legacy function for fetching subreddit titles via user input.

    This function is kept for backward compatibility with older code.
    It prompts the user for a subreddit name and returns post titles.

    Returns:
        list[str]: List of post titles from the specified subreddit

    Deprecated:
        Use RedditScraper class instead for better error handling and flexibility
    """
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}

    # Prompt user for subreddit name
    subreddit_name = input('Enter subreddit name: ')
    url = f"https://www.reddit.com/r/{subreddit_name}/hot.json?limit=50"

    # Fetch data
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    children = data["data"]["children"]

    # Extract and clean titles
    clean_titles = []
    for post in children:
        title = post["data"]["title"]
        # Remove newlines and extra whitespace
        cleaned = title.replace("\n", " ").strip()
        clean_titles.append(cleaned)

    return clean_titles
