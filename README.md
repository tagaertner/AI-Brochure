# 🧠 AI Brochure Generator

Generate professional or humorous brochures from any public company website using OpenAI, Python, and web scraping.

## ✨ Features

- Scrapes company websites to extract landing page text and relevant subpages
- Uses OpenAI (GPT-4o) to generate brochures in markdown
- Supports both **serious** and **humorous** brochure tones
- CLI-based interface with clear prompts
- Saves the brochure as a `.md` file for easy use or publishing

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tagaertner/AI-Brochure.git
cd AI-Brochure
```

### 2. Set up your environment

Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt

### 3. Add your OpenAI API key

Create a .env file in the project root:
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx

### 💻 Running the App

Run the CLI script:
python main.py

📝 Example Output

Serious tone:

Hugging Face is a collaborative machine learning platform trusted by companies like Google and Microsoft…

Humorous tone:

Hugging Face: Where AI meets hugs and GPUs are our love language 💻💖

## 🛠 Tech Stack

- Python 3.10+
- OpenAI API (GPT-4o)
- BeautifulSoup (HTML parsing)
- python-dotenv (environment config)
