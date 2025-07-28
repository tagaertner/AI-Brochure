import os
import requests
import json
import validators
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI
from urllib.parse import urljoin, urlparse

# Load API key
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if api_key and api_key.startswith('sk-proj-') and len(api_key) > 10:
    print("API key looks good so far! 👍")
else:
    print("There might be a problem with your API key. 🧐")

MODEL = 'gpt-4o-mini'
openai = OpenAI()

# Pretend we're a browser so we don't get blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    """Utility class to scrape a webpage for text and links"""
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"

        # Protects agaist 404 or server errors
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if soup.body:
            for tag in soup.body(["script", "style", "img", "input"]):
                tag.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""

        self.links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href and not href.startswith(('mailto:', '#')):
                full_url = urljoin(self.url, href)
                self.links.append(full_url)

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

    def __str__(self):
        return self.get_contents()
    
class BrochureGenerator:
    
    def __init__(self, model='gpt-4o-mini'):
        self.model = model
        self.openai = OpenAI()
            # Prompt templates
        self.link_system_prompt = link_system_prompt = """
            You are provided with a list of links found on a webpage. 
            Return only the most relevant links to include in a company brochure: e.g. About, Company, or Careers/Jobs pages.

            Respond ONLY with raw JSON (no explanation, no markdown, no code blocks). Example:
            {
            "links": [
                {"type": "about page", "url": "https://full.url/about"},
                {"type": "careers page", "url": "https://full.url/careers"}
            ]
                    }
            """.strip()
        self.serious_system_prompt = serious_system_prompt ="""
            You are an assistant that analyzes the contents of several relevant pages from a company website
            and creates a short, professional brochure about the company for prospective customers, investors, and recruits. Respond in markdown.
            Include details of company culture, customers, and careers/jobs if available.
            """.strip()

        self.humorous_system_prompt = humorous_system_prompt="""
            You're a witty assistant who turns boring company content into a fun, humorous brochure.
            Keep it light, clever, and engaging — like a marketing campaign written by a comedian who understands tech.
            Respond in markdown. Sprinkle in emojis, jokes, and casual tone — but still convey useful info.
            """.strip()
            
    def extract_company_name(self,url):
        netloc = urlparse(url).netloc
        parts = netloc.split(".")
        for part in parts:
            if part.lower() not in ("www", "com", "org", "net"):
                return part.capitalize()
        return "Company"


        # Prompt construction helpers
    def get_links_user_prompt(self,website):
        user_prompt = f"Here is the list of links on the website of {website.url}:\n"
        user_prompt += "Please return the relevant links for a company brochure in raw JSON.\n"
        user_prompt += "\n".join(website.links)
        return user_prompt

    def get_links(self,url):
        website = Website(url)
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": self.link_system_prompt},
                {"role": "user", "content": self.get_links_user_prompt(website)}
            ]
        )
        result = response.choices[0].message.content
        # print("Raw OpenAI response for links:\n", result)

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            print("⚠️ Failed to parse JSON from OpenAI response.")
            return {"links": []}

    def get_all_details(self,url):
        result = "Landing page:\n"
        result += Website(url).get_contents()
        links = self.get_links(url)

        if not links["links"]:
            result += "\n\nNo additional relevant links were found.\n"
            return result

        for link in links["links"]:
            result += f"\n\n{link['type'].capitalize()}:\n"
            result += Website(link["url"]).get_contents()
        return result

    def get_brochure_user_prompt(self,company_name, url):
        user_prompt = f"You are looking at a company called: {company_name}\n"
        user_prompt += "Here are the contents of its landing page and other relevant pages. Use this to create a markdown brochure.\n"
        user_prompt += self.get_all_details(url)
        return user_prompt[:5000]  # Truncate if needed

    def create_brochure(self,company_name, url, tone="serious"):
        print(f"\n🔍 Generating a {tone} brochure for {company_name}...\n")

        system_prompt = self.serious_system_prompt if tone == "serious" else self.humorous_system_prompt

        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self.get_brochure_user_prompt(company_name, url)}
            ]
        )

        result = response.choices[0].message.content
        print("\n📝 --- Brochure ---\n")
        print(result)

        filename = f"{company_name.lower()}_brochure_{tone}.md"
        with open(filename, "w") as f:
            f.write(result)
        print(f"\n✅ Brochure saved to: {filename}")

# Validate if user gave a valid url
def is_valid_url(url):
    return validators.url(url)

# CLI runner
if __name__ == "__main__":
    url = input("the full URL of the website you'd like to create a brochure from: ").strip()
    
    if not is_valid_url(url):
        print("❌ That does not look like a valid URL. Please try again")
    try:
        requests.head(url, headers=headers, timeout=5)
    except requests.RequestException as e:
        print(f"❌ Could not connect to the website: {e}")
        exit(1)
        
    tone = input("What tone do you want for the brochure? (serious or humorous): ").strip().lower()

    if tone not in ("serious", "humorous"):
        print("⚠️ Invalid tone selected. Defaulting to serious.")
        tone = "serious"
    
    # Create instanct to call the  BrochureGenerator class
    generator = BrochureGenerator()

    company_name = generator.extract_company_name(url)
    generator.create_brochure(company_name, url, tone)