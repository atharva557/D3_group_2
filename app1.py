# from flask import Flask, render_template, request, redirect, url_for, flash, session
# from DB import RedditDatabase
# from RedditEmotionAnalyzer import RedditEmotionAnalyzer
# from get_titles import RedditScraper
# from util import generate_otp,send_otp_email
# scraper = RedditScraper()
#
#
#
#
#
#
#
#
#
#
# analyzer = RedditEmotionAnalyzer(model_path="./best_reddit_model_2")
# app = Flask(__name__)
# app.secret_key = "secret_key_for_session" # Needed for flash messages
# db = RedditDatabase()
#
# @app.route('/')
# def login_page():
#     return render_template('login.html')
#
# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form.get('username')
#     password = request.form.get('password')
#
#     user_id = db.verify_login(username, password)
#
#     if user_id:
#         session['user_id'] = user_id
#         #return f"Login Successful! Welcome user ID: {user_id}"
#         return redirect(url_for('dashboard'))
#
#     else:
#         flash("Invalid username or password")
#         return redirect(url_for('login_page'))
#
# @app.route('/signup')
# def signup_page():
#     return render_template('signup.html')
#
#
#
# @app.route('/send_otp', methods=['POST'])
# def send_otp_route():
#     data = request.get_json()
#     email = data.get('email')
#
#     if not email:
#         return {"success": False, "message": "Email is required"}
#
#     # 1. Generate & Save to Session
#     otp = generate_otp()
#     session['current_otp'] = otp
#     session['otp_email'] = email
#
#     # 2. Send Email
#     if send_otp_email(email, otp):
#         return {"success": True}  # JS expects this JSON
#     else:
#         return {"success": False, "message": "Failed to send email"}
#
#
# @app.route('/register', methods=['POST'])
# def register():
#     # 1. Get Form Data
#     username = request.form.get('username')
#     email = request.form.get('email')
#     password = request.form.get('password')
#     user_otp = request.form.get('otp')  # The hidden field
#
#     # 2. Validation
#     real_otp = session.get('current_otp')
#     saved_email = session.get('otp_email')
#
#     if not real_otp or user_otp != real_otp:
#         flash("Incorrect OTP. Please try again.")
#         return redirect(url_for('signup_page'))
#
#     if email != saved_email:
#         flash("Email mismatch. Please do not change your email.")
#         return redirect(url_for('signup_page'))
#
#     # 3. Add to Database
#     # Make sure your DB.py 'add_user' function accepts email!
#     user_id = db.add_user(username, email, password)
#
#     if user_id:
#         session.clear()  # Clear OTP data
#         flash("Account created! Please log in.")
#         return redirect(url_for('login_page'))
#     else:
#         flash("Username or Email already taken.")
#         return redirect(url_for('signup_page'))
#
#
#
# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session:
#         return redirect(url_for('login_page'))
#     return render_template('dashboard.html')
#
# @app.route('/reddit_options')
# def reddit_options():
#     if 'user_id' not in session:
#         return redirect(url_for('login_page'))
#     return render_template('reddit_options.html')
#
# @app.route('/analyze_own')
# def analyze_own():
#     # This will eventually lead to a simple text box page
#     return render_template("analyze_own.html")
#
#
# @app.route('/input_query')
# def input_query():
#     return render_template('input_query.html')
#
#
# @app.route('/run_analysis', methods=['POST'])
# def run_analysis():
#     if 'user_id' not in session:
#         return redirect(url_for('login_page'))
#
#     search_type = request.form.get('search_type')
#     query_text = request.form.get('query_input')
#
#     # 1. Scrape data (NOW returns 2 items)
#     scraped_items, full_raw_json = scraper.fetch_data(search_type, query_text)
#
#     if not scraped_items:
#         return "No posts found to analyze. Please try a different search."
#
#     # 2. Analyze data
#     texts = [item['text'] for item in scraped_items]
#     ai_results = analyzer.analyze_batch(texts)
#
#     # 3. Save to Database (Pass the full_raw_json now)
#     type_map = {'1': 'subreddit', '2': 'topic', '3': 'user'}
#
#     search_id = db.add_search_event(
#         session['user_id'],
#         query_text,
#         type_map[search_type],
#         full_raw_json  # <--- Pass the raw JSON here
#     )
#
#     # 4. Save Results (Keep existing logic)
#     final_db_data = []
#     for i, res in enumerate(ai_results):
#         final_db_data.append({
#             'link': scraped_items[i]['link'],
#             'text': res['content'],
#             'sentiment': res['sentiment'],
#             'primary_emotion': res['primary_emotion'],
#             'confidence': res['confidence'],
#             'raw_dict': res['raw_json']
#         })
#     db.add_analysis_results(search_id, final_db_data)
#     if search_type == '1':
#         # Calculate overall stats
#         overall_emotion = analyzer.get_dominant_emotion_from_batch(ai_results)
#         overall_sentiment = analyzer.get_sentiment(overall_emotion)
#
#         # Update the cache silently in the background
#         db.update_subreddit_vibe(query_text, overall_sentiment, overall_emotion)
#
#     return render_template('results.html', results=ai_results, query=query_text)
#
#
# @app.route('/analyze_own')
# def analyze_own_page():
#     if 'user_id' not in session:
#         return redirect(url_for('login_page'))
#     return render_template('analyze_own.html')
#
#
# @app.route('/process_statement', methods=['POST'])
# def process_statement():
#     if 'user_id' not in session:
#         return redirect(url_for('login_page'))
#
#     statement = request.form.get('statement')
#
#     # 1. Analyze
#     result = analyzer.predict(statement)
#     # 2. Save to DB (New logic)
#     # We log this as a "statement" type search
#     search_id = db.add_search_event(session['user_id'], statement, "statement", None)
#     # Prepare the result for the DB (needs to match the list format expected by add_analysis_results)
#     db_data = [{
#         'link': 'Direct Statement',  # No URL for direct text
#         'content': result['content'],
#         'sentiment': result['sentiment'],
#         'primary_emotion': result['primary_emotion'],
#         'confidence': result['confidence'],
#         'raw_json': result['raw_json']
#     }]
#
#     db.add_analysis_results(search_id, db_data)
#
#     # 3. Show Results
#     return render_template('results.html', results=[result], query="Your Statement")
#
# # Change this line:
# # def analyze_post():
#
# # To this:
# @app.route('/analyze_post')
# def analyze_post_page():   # <--- Updated name
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     return render_template("analyze_post.html")
#
#
# @app.route('/check_vibe', methods=['POST'])
# def check_vibe():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#
#     subreddit_name = request.form.get('subreddit').strip()  # Remove spaces
#     draft_text = request.form.get('post_content')
#
#     # ======================================================
#     # PART 1: Analyze the User (Always needs to be done fresh)
#     # ======================================================
#     user_result = analyzer.predict(draft_text)
#     user_emotion = user_result['primary_emotion']
#
#     # ======================================================
#     # PART 2: Get Subreddit Vibe (The Smart Cache System)
#     # ======================================================
#
#     # A. Check Database First
#     cached_vibe = db.get_subreddit_vibe(subreddit_name)
#
#     if cached_vibe:
#         # HIT! We found it in the DB. Use the stored data.
#         print(f"⚡ CACHE HIT: Using stored vibe for r/{subreddit_name}")
#         sub_emotion = cached_vibe['overall_emotion']
#         # We don't strictly need sentiment for the score, but we have it if needed
#         # sub_sentiment = cached_vibe['overall_sentiment']
#
#     else:
#         # MISS! We need to scrape and analyze.
#         print(f"🐢 CACHE MISS: Scraping r/{subreddit_name}...")
#
#         # 1. Scrape (ignoring raw json for vibe check)
#         raw_posts, _ = scraper.fetch_data("1", subreddit_name)
#
#         if not raw_posts:
#             sub_emotion = "neutral"  # Fallback if empty/banned
#         else:
#             # 2. Analyze Batch
#             texts = [p['text'] for p in raw_posts]
#             batch_results = analyzer.analyze_batch(texts)
#
#             # 3. Calculate Dominant Emotion
#             sub_emotion = analyzer.get_dominant_emotion_from_batch(batch_results)
#             sub_sentiment = analyzer.get_sentiment(sub_emotion)
#
#             # 4. SAVE TO CACHE (So the next person gets it instantly)
#             db.update_subreddit_vibe(subreddit_name, sub_sentiment, sub_emotion)
#
#     # ======================================================
#     # PART 3: Calculate Compatibility (Your Logic)
#     # ======================================================
#     score = 50
#     u_emo = user_emotion.lower()
#     s_emo = sub_emotion.lower()
#
#     # Define groups
#     positives = {'joy', 'love', 'optimism', 'admiration', 'gratitude', 'amusement', 'excitement', 'pride', 'relief',
#                  'caring', 'approval', 'desire'}
#     negatives = {'anger', 'disgust', 'fear', 'sadness', 'annoyance', 'disappointment', 'embarrassment', 'grief',
#                  'nervousness', 'remorse', 'disapproval'}
#
#     if u_emo == s_emo:
#         score = 98
#     elif u_emo in positives and s_emo in positives:
#         score = 85
#     elif u_emo in negatives and s_emo in negatives:
#         score = 80
#     elif (u_emo in positives and s_emo in negatives) or (u_emo in negatives and s_emo in positives):
#         score = 25
#
#     return render_template('vibe_result.html', score=score, subreddit=subreddit_name, user_emotion=user_emotion,
#                            sub_emotion=sub_emotion)
#
#
#
#
#
# @app.route('/history')
# def history():
#     if 'user_id' not in session:
#         return redirect(url_for('login_page'))
#
#     # Fetch all searches for the current user
#     user_history = db.get_searches_by_user_id(session['user_id'])
#     return render_template('history.html', history=user_history)
#
# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login_page'))
#
#
# if __name__ == "__main__":
#     app.run(debug=True)


"""
Reddit Pulse - Main Flask Application
======================================
This module contains all Flask routes and application logic for the Reddit Pulse
sentiment analysis web application. It handles user authentication, Reddit data
analysis, and result presentation.

Author: Reddit Pulse Team
License: MIT
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from DB import RedditDatabase
from RedditEmotionAnalyzer import RedditEmotionAnalyzer
from get_titles import RedditScraper
from util import generate_otp, send_otp_email

# Initialize core components
scraper = RedditScraper()
analyzer = RedditEmotionAnalyzer(model_path="./best_reddit_model")
app = Flask(__name__)
app.secret_key = "secret_key_for_session"  # Needed for flash messages
db = RedditDatabase()


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def login_page():
    """
    Render the login page.

    Returns:
        str: Rendered HTML template for login page
    """
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    """
    Process user login credentials and establish session.

    Form Parameters:
        username (str): User's username
        password (str): User's password

    Returns:
        Response: Redirect to dashboard on success, or back to login with error message
    """
    username = request.form.get('username')
    password = request.form.get('password')

    user_id = db.verify_login(username, password)

    if user_id:
        session['user_id'] = user_id
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid username or password")
        return redirect(url_for('login_page'))


@app.route('/signup')
def signup_page():
    """
    Render the signup page for new user registration.

    Returns:
        str: Rendered HTML template for signup page
    """
    return render_template('signup.html')


@app.route('/send_otp', methods=['POST'])
def send_otp_route():
    """
    Generate and send a one-time password (OTP) to user's email for verification.

    JSON Parameters:
        email (str): User's email address

    Returns:
        dict: JSON response with success status and optional error message

    Session Variables Set:
        current_otp (str): Generated 4-digit OTP code
        otp_email (str): Email address the OTP was sent to
    """
    data = request.get_json()
    email = data.get('email')

    if not email:
        return {"success": False, "message": "Email is required"}

    # Generate OTP and save to session for verification
    otp = generate_otp()
    session['current_otp'] = otp
    session['otp_email'] = email

    # Send OTP via email
    if send_otp_email(email, otp):
        return {"success": True}
    else:
        return {"success": False, "message": "Failed to send email"}


@app.route('/register', methods=['POST'])
def register():
    """
    Process new user registration after OTP verification.

    Form Parameters:
        username (str): Desired username
        email (str): User's email address
        password (str): User's password
        otp (str): OTP code from verification email

    Returns:
        Response: Redirect to login on success, or back to signup with error message

    Validation:
        - Verifies OTP matches session-stored value
        - Ensures email hasn't been changed since OTP was sent
        - Checks username/email uniqueness in database
    """
    # Extract form data
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    user_otp = request.form.get('otp')

    # Validate OTP
    real_otp = session.get('current_otp')
    saved_email = session.get('otp_email')

    if not real_otp or user_otp != real_otp:
        flash("Incorrect OTP. Please try again.")
        return redirect(url_for('signup_page'))

    if email != saved_email:
        flash("Email mismatch. Please do not change your email.")
        return redirect(url_for('signup_page'))

    # Add user to database
    user_id = db.add_user(username, email, password)

    if user_id:
        session.clear()  # Clear OTP data for security
        flash("Account created! Please log in.")
        return redirect(url_for('login_page'))
    else:
        flash("Username or Email already taken.")
        return redirect(url_for('signup_page'))


@app.route('/logout')
def logout():
    """
    Log out the current user by clearing their session.

    Returns:
        Response: Redirect to login page
    """
    session.clear()
    return redirect(url_for('login_page'))


# ============================================================================
# DASHBOARD & NAVIGATION ROUTES
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """
    Render the main dashboard (home page for logged-in users).

    Returns:
        Response: Dashboard template or redirect to login if not authenticated

    Session Requirements:
        user_id: Must be present to access this page
    """
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')


@app.route('/reddit_options')
def reddit_options():
    """
    Display analysis options page (Subreddit, Topic, or User analysis).

    Returns:
        Response: Reddit options template or redirect to login if not authenticated
    """
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('reddit_options.html')


@app.route('/input_query')
def input_query():
    """
    Render the input form for Reddit analysis queries.

    Query Parameters:
        type (str): Analysis type ('1'=subreddit, '2'=topic, '3'=user)

    Returns:
        str: Rendered input query template
    """
    return render_template('input_query.html')


@app.route('/history')
def history():
    """
    Display user's analysis history.

    Returns:
        Response: History template with past searches, or redirect to login

    Template Variables:
        history (list): List of previous search events for current user
    """
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_history = db.get_searches_by_user_id(session['user_id'])
    return render_template('history.html', history=user_history)


# ============================================================================
# REDDIT ANALYSIS ROUTES
# ============================================================================

@app.route('/run_analysis', methods=['POST'])
def run_analysis():
    """
    Execute full Reddit data analysis pipeline.

    This route performs the following steps:
    1. Scrapes Reddit data based on search type and query
    2. Analyzes scraped content using fine-tuned BERT model
    3. Saves search event and results to database
    4. Updates subreddit vibe cache (for subreddit searches)
    5. Displays results to user

    Form Parameters:
        search_type (str): Type of search ('1'=subreddit, '2'=topic, '3'=user)
        query_input (str): The search query (subreddit name, topic, or username)

    Returns:
        Response: Results page with analysis data, or error message if no data found

    Database Operations:
        - Adds search_event record
        - Adds analysis_results records
        - Updates subreddit_vibes cache (if applicable)
    """
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    search_type = request.form.get('search_type')
    query_text = request.form.get('query_input')

    # Step 1: Scrape Reddit data
    scraped_items, full_raw_json = scraper.fetch_data(search_type, query_text)

    if not scraped_items:
        return render_template('no_content.html', query=query_text)

    # Step 2: Analyze content with AI model
    texts = [item['text'] for item in scraped_items]
    ai_results = analyzer.analyze_batch(texts)

    # Step 3: Save search event to database
    type_map = {'1': 'subreddit', '2': 'topic', '3': 'user'}
    search_id = db.add_search_event(
        session['user_id'],
        query_text,
        type_map[search_type],
        full_raw_json
    )

    # Step 4: Save individual analysis results
    final_db_data = []
    for i, res in enumerate(ai_results):
        final_db_data.append({
            'link': scraped_items[i]['link'],
            'text': res['content'],
            'sentiment': res['sentiment'],
            'primary_emotion': res['primary_emotion'],
            'confidence': res['confidence'],
            'raw_json': res['raw_json']
        })
    db.add_analysis_results(search_id, final_db_data)

    # Step 5: Update subreddit vibe cache (optimization for future vibe checks)
    if search_type == '1':
        overall_emotion = analyzer.get_dominant_emotion_from_batch(ai_results)
        overall_sentiment = analyzer.get_sentiment(overall_emotion)
        db.update_subreddit_vibe(query_text, overall_sentiment, overall_emotion)

    return render_template('results.html', results=ai_results, query=query_text)


# ============================================================================
# PERSONAL STATEMENT ANALYSIS
# ============================================================================

@app.route('/analyze_own')
def analyze_own():
    """
    Render the personal statement analysis page.

    Returns:
        Response: Statement analysis template or redirect to login
    """
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('analyze_own.html')


@app.route('/process_statement', methods=['POST'])
def process_statement():
    """
    Analyze a user's personal statement for emotional content.

    Form Parameters:
        statement (str): User's text input to analyze

    Returns:
        Response: Results page showing emotion and sentiment analysis

    Database Operations:
        - Logs statement as a search event
        - Saves analysis result
    """
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    statement = request.form.get('statement')

    # Analyze the statement
    result = analyzer.predict(statement)
    print(result)

    # Save to database as 'statement' type search
    search_id = db.add_search_event(session['user_id'], statement, "statement", None)

    # Format result for database insertion
    db_data = [{
        'link': 'Direct Statement',
        'content': result['content'],
        'sentiment': result['sentiment'],
        'primary_emotion': result['primary_emotion'],
        'confidence': result['confidence'],
        'raw_json': result['raw_json']
    }]

    db.add_analysis_results(search_id, db_data)

    return render_template('results.html', results=[result], query="Your Statement")


# ============================================================================
# VIBE CHECK (POST COMPATIBILITY)
# ============================================================================

@app.route('/analyze_post')
def analyze_post_page():
    """
    Render the vibe check page for testing post compatibility with a subreddit.

    Returns:
        Response: Vibe check template or redirect to login
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("analyze_post.html")


@app.route('/check_vibe', methods=['POST'])
def check_vibe():
    """
    Check if a draft post's emotional tone matches a subreddit's community vibe.

    This feature uses an intelligent caching system:
    - First checks database for recently analyzed subreddit vibes
    - If not cached, scrapes and analyzes subreddit in real-time
    - Saves result to cache for future instant lookups

    Form Parameters:
        subreddit (str): Target subreddit name
        post_content (str): User's draft post text

    Returns:
        Response: Vibe result page with compatibility score and recommendations

    Compatibility Scoring Algorithm:
        - 98%: Exact emotion match
        - 85%: Both positive emotions
        - 80%: Both negative emotions
        - 50%: Baseline (no strong correlation)
        - 25%: Conflicting sentiment (positive vs negative)
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    subreddit_name = request.form.get('subreddit').strip()
    draft_text = request.form.get('post_content')

    # PART 1: Analyze user's draft post
    user_result = analyzer.predict(draft_text)
    user_emotion = user_result['primary_emotion']

    # PART 2: Get subreddit vibe (with intelligent caching)
    cached_vibe = db.get_subreddit_vibe(subreddit_name)

    if cached_vibe:
        # Cache hit - use stored vibe data
        print(f"⚡ CACHE HIT: Using stored vibe for r/{subreddit_name}")
        sub_emotion = cached_vibe['overall_emotion']
    else:
        # Cache miss - scrape and analyze subreddit
        print(f"🐢 CACHE MISS: Scraping r/{subreddit_name}...")

        raw_posts, _ = scraper.fetch_data("1", subreddit_name)

        if not raw_posts:
            sub_emotion = "neutral"  # Fallback for empty/banned subreddits
        else:
            # Analyze batch of posts
            texts = [p['text'] for p in raw_posts]
            batch_results = analyzer.analyze_batch(texts)

            # Calculate dominant emotion
            sub_emotion = analyzer.get_dominant_emotion_from_batch(batch_results)
            sub_sentiment = analyzer.get_sentiment(sub_emotion)

            # Save to cache for future lookups
            db.update_subreddit_vibe(subreddit_name, sub_sentiment, sub_emotion)

    # PART 3: Calculate compatibility score
    score = 50  # Baseline score
    u_emo = user_emotion.lower()
    s_emo = sub_emotion.lower()

    # Define emotion groups for scoring
    positives = {
        'joy', 'love', 'optimism', 'admiration', 'gratitude', 'amusement',
        'excitement', 'pride', 'relief', 'caring', 'approval', 'desire'
    }
    negatives = {
        'anger', 'disgust', 'fear', 'sadness', 'annoyance', 'disappointment',
        'embarrassment', 'grief', 'nervousness', 'remorse', 'disapproval'
    }

    # Scoring logic
    if u_emo == s_emo:
        # Perfect match - same specific emotion
        score = 98
    elif u_emo in positives and s_emo in positives:
        # Both positive (good compatibility)
        score = 85
    elif u_emo in negatives and s_emo in negatives:
        # Both negative (compatible tone)
        score = 80
    elif (u_emo in positives and s_emo in negatives) or (u_emo in negatives and s_emo in positives):
        # Conflicting sentiment (poor match)
        score = 25

    return render_template(
        'vibe_result.html',
        score=score,
        subreddit=subreddit_name,
        user_emotion=user_emotion,
        sub_emotion=sub_emotion
    )


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app.run(debug=True)
