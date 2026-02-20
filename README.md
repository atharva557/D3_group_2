# Reddit Pulse 🎯

> **AI-Powered Emotion Analysis for Reddit**  
> Analyze the emotional pulse of Reddit communities, topics, and individual posts using fine-tuned BERT models.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [API Documentation](#api-documentation)
- [Training Your Own Model](#training-your-own-model)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

**Reddit Pulse** is a full-stack web application that uses state-of-the-art natural language processing (NLP) to analyze emotions in Reddit posts and comments. Built with a fine-tuned BERT model trained on the GoEmotions dataset, it can detect 28 distinct emotions across 4 sentiment categories.

### What Can You Do?

- **Analyze Subreddits**: Understand the emotional tone of entire communities
- **Search Topics**: Track emotional trends across Reddit for specific keywords
- **Profile Users**: Analyze a user's emotional patterns and engagement style
- **Personal Analysis**: Check your own text for emotional content
- **Vibe Check**: Test if your post matches a subreddit's community mood before posting

---

## ✨ Key Features

### 🎭 Advanced Emotion Detection
- **28 Emotion Labels**: joy, anger, sadness, love, fear, surprise, and 22 more
- **4 Sentiment Categories**: positive, negative, ambiguous, neutral
- **Multi-Label Classification**: Detects multiple emotions in a single text

### 🔐 User Authentication
- Secure email-based registration with OTP verification
- Password hashing with SHA-256
- Session management for personalized experiences

### 📊 Intelligent Analysis
- **Batch Processing**: Analyze up to 25 posts/comments at once
- **Smart Caching**: Subreddit vibes cached to reduce redundant analysis
- **Real-time Scraping**: Fetches live data from Reddit's public API

### 🎨 Modern UI/UX
- **Dark/Light Mode**: Automatic theme switching with system preference detection
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Interactive Charts**: Visualize emotion distributions with Chart.js
- **Toast Notifications**: Non-intrusive user feedback

### 📈 History Tracking
- View all your past analyses
- Track emotional trends over time
- Export results for further analysis

---

## 🛠️ Tech Stack

### Backend
- **Flask 2.0+**: Lightweight web framework
- **SQLite**: Database for users, searches, and results
- **PyTorch 2.0+**: Deep learning framework
- **Transformers (Hugging Face)**: BERT model implementation

### Frontend
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla JavaScript**: No heavy frameworks, pure performance
- **Chart.js**: Beautiful data visualizations

### AI/ML
- **BERT**: Bidirectional Encoder Representations from Transformers
- **GoEmotions Dataset**: 58K Reddit comments labeled with emotions
- **Custom Fine-Tuning**: Optimized for Reddit's informal language

---

## 📥 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- (Optional) NVIDIA GPU with CUDA for faster training/inference

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/reddit-pulse.git
cd reddit-pulse
```

### Step 2: Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required Packages:**
```
flask>=2.0.0
torch>=2.0.0
transformers>=4.30.0
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.2.0
matplotlib>=3.7.0
requests>=2.28.0
```

### Step 4: Download Pre-trained Model

Option A: **Use Our Pre-trained Model** (Recommended)
```bash
# Download from Google Drive/Hugging Face
# Extract to ./best_reddit_model/
```

Option B: **Train Your Own Model** (See [Training Your Own Model](#training-your-own-model))

### Step 5: Initialize Database

```bash
python -c "from DB import RedditDatabase; RedditDatabase()"
```

This creates `reddit_pulse.db` with all required tables.

### Step 6: Configure Email (For OTP Verification)

Edit `util.py` and replace with your credentials:

```python
sender = "your-email@gmail.com"
password = "your-app-password"  # Use Gmail App Password
```

> **Security Note**: For production, use environment variables:
> ```python
> import os
> sender = os.getenv('EMAIL_SENDER')
> password = os.getenv('EMAIL_PASSWORD')
> ```

---

## 🚀 Usage

### Running the Application

```bash
python app1.py
```

The app will start at `http://127.0.0.1:5000`

### Quick Start Guide

1. **Create an Account**
   - Navigate to `/signup`
   - Enter email, username, and password
   - Verify email with OTP code

2. **Log In**
   - Go to `/` (login page)
   - Enter credentials

3. **Analyze Reddit Data**
   - **Subreddit Analysis**: Analyze → Subreddit → Enter `python` → Analyze
   - **Topic Search**: Analyze → Topic → Enter `machine learning` → Analyze
   - **User Profile**: Analyze → User → Enter username → Analyze

4. **Personal Statement**
   - Analyze → Statement → Type your text → Analyze

5. **Vibe Check**
   - Analyze → Post → Enter subreddit and draft post → Check Compatibility

---

## 📁 Project Structure

```
reddit-pulse/
│
├── app1.py                    # Main Flask application
├── DB.py                      # Database management
├── RedditEmotionAnalyzer.py   # AI model inference
├── get_titles.py              # Reddit scraper
├── util.py                    # Utility functions (OTP, email)
├── train.py                   # Model fine-tuning script
├── pretrain.py                # BERT pre-training script
│
├── best_reddit_model/         # Trained model directory
│   ├── pytorch_model.bin      # Model weights
│   ├── config.json            # Model configuration
│   ├── vocab.txt              # BERT vocabulary
│   └── labels.csv             # Emotion labels
│
├── templates/                 # HTML templates
│   ├── dashboard.html
│   ├── login.html
│   ├── signup.html
│   ├── analyze_own.html
│   ├── analyze_post.html
│   ├── input_query.html
│   ├── results.html
│   ├── history.html
│   ├── vibe_result.html
│   └── reddit_options.html
│
├── static/                    # Static assets
│   ├── css/
│   │   └── theme-variables.css
│   └── js/
│       ├── theme-manager.js
│       ├── navbar.js
│       ├── toast.js
│       └── tailwind-config.js
│
├── reddit_pulse.db            # SQLite database (auto-generated)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🧠 How It Works

### Architecture Overview

```
User Input → Reddit Scraper → BERT Tokenizer → Fine-tuned BERT Model → Emotion Predictions → Database → Results Page
```

### 1. Data Collection (Reddit Scraper)

The `RedditScraper` class fetches data from Reddit's public JSON API:

```python
scraper = RedditScraper()
posts, raw_json = scraper.fetch_data('1', 'python')  # Fetch r/python
```

**Supported Modes:**
- Mode 1: Subreddit (`r/subredditname`)
- Mode 2: Topic search (keyword-based)
- Mode 3: User profile (`u/username`)

### 2. Text Preprocessing

Text is cleaned and tokenized using BERT's tokenizer:

```python
inputs = tokenizer(text, max_length=128, truncation=True, padding=True)
```

### 3. Emotion Prediction

The fine-tuned BERT model predicts emotions:

```python
with torch.no_grad():
    outputs = model(**inputs)
    probs = torch.sigmoid(outputs.logits)
```

### 4. Dynamic Thresholding

Different emotions use different confidence thresholds:

- **Neutral**: 0.85 (strict)
- **Strong emotions** (fear, anger): 0.10 (sensitive)
- **Others**: 0.05 (standard)

### 5. Sentiment Mapping

Emotions are grouped into sentiments:

| Sentiment  | Emotions |
|------------|----------|
| Positive   | joy, love, gratitude, admiration, pride, relief, etc. |
| Negative   | anger, sadness, fear, disgust, disappointment, etc. |
| Ambiguous  | confusion, surprise, curiosity, realization |
| Neutral    | neutral |

---

## 📡 API Documentation

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Search Events Table
```sql
CREATE TABLE search_events (
    search_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    query_text TEXT NOT NULL,
    search_type TEXT NOT NULL,  -- 'subreddit', 'topic', 'user', 'statement'
    raw_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
```

#### Analysis Results Table
```sql
CREATE TABLE analysis_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER NOT NULL,
    link TEXT,
    content TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    primary_emotion TEXT NOT NULL,
    confidence REAL NOT NULL,
    raw_emotions_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (search_id) REFERENCES search_events (search_id)
);
```

#### Subreddit Vibes Cache
```sql
CREATE TABLE subreddit_vibes (
    vibe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subreddit_name TEXT UNIQUE NOT NULL,
    overall_sentiment TEXT NOT NULL,
    overall_emotion TEXT NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎓 Training Your Own Model

### Step 1: Pre-train on Reddit Data (Optional but Recommended)

```bash
# Collect 50K Reddit titles
python scraper_bulk.py  # (Not included - create your own)

# Pre-train BERT on Reddit slang
python pretrain.py
```

**What This Does:**
- Teaches BERT Reddit-specific vocabulary
- Improves understanding of informal language
- Uses Masked Language Modeling (MLM)

### Step 2: Fine-tune on GoEmotions

```bash
# Download GoEmotions dataset
# https://github.com/google-research/google-research/tree/master/goemotions

# Fine-tune on emotions
python train.py
```

**Training Details:**
- **Dataset**: 58,000 Reddit comments
- **Epochs**: 4
- **Batch Size**: 16
- **Learning Rate**: 2e-5
- **Optimizer**: AdamW

**Output:**
- `./best_reddit_model/`: Your custom model
- `training_results.png`: Loss curves

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs
Open an issue with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)

### Feature Requests
Open an issue with:
- Clear description of the feature
- Use case/motivation
- Proposed implementation (optional)

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Research**: For the GoEmotions dataset
- **Hugging Face**: For the Transformers library
- **PyTorch Team**: For the deep learning framework
- **Reddit**: For providing public JSON APIs

---

## 📧 Contact

**Project Maintainer**: Reddit Pulse Team  
**Email**: redditpulse55@gmail.com  
**GitHub**: [github.com/yourusername/reddit-pulse](https://github.com/yourusername/reddit-pulse)

---

## 🎯 Roadmap

- [ ] Add support for more social media platforms (Twitter, Facebook)
- [ ] Implement real-time emotion tracking dashboards
- [ ] Add emotion timeline visualization
- [ ] Create browser extension for instant vibe checks
- [ ] Integrate with Reddit API for authenticated access
- [ ] Add export to CSV/JSON functionality
- [ ] Implement user emotion profiles
- [ ] Add A/B testing for post optimization

---

**Made with ❤️ by the Reddit Pulse Team**
