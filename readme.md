# README.md

# Aura - Carbon Footprint Tracker

Aura is a web application that helps users analyze the environmental impact of everyday products by scanning ingredient lists, leveraging AI-powered analysis, and tracking sustainability progress. Make eco-friendly choices and join a community of conscious consumers!

## Features

- **Ingredient Analysis:** Enter or scan product ingredients to receive instant environmental impact ratings.
- **AI-Powered Insights:** Get detailed analysis and suggestions for eco-friendly alternatives.
- **Progress Tracking:** Monitor your points, streaks, and leaderboard rank.
- **OCR Scanning:** Upload product label images for automatic ingredient extraction.
- **User Profiles:** Manage your account, avatar, and view personal statistics.
- **Leaderboards:** Compete with others and climb the sustainability leaderboard.

## Getting Started

### Prerequisites

- Python 3.10+
- [pip](https://pip.pypa.io/en/stable/)
- (Optional) [virtualenv](https://virtualenv.pypa.io/en/latest/)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/aura-pro.git
   cd aura-pro
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your API keys (GROQ, OCR, Google OAuth, etc).

4. **Initialize the database:**
   ```sh
   python database.py init
   ```

5. **(Optional) Add sample data:**
   ```sh
   python database.py sample
   ```

### Running the Application

```sh
python run.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

## Usage

- **Analyze Products:** Go to the dashboard and click "Analyze Product". Enter ingredients or upload a label image.
- **View Results:** Get instant feedback, points, and eco-friendly suggestions.
- **Track Progress:** Check your stats, streaks, and leaderboard position.
- **Profile Settings:** Update your username, email, and avatar in the profile section.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements.

## License

This project is licensed under the MIT License.

---

**Aura** – Making sustainability accessible to everyone.