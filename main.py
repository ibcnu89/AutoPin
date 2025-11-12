import requests
import base64
from openai import OpenAI
import os

# Load from environment (set in Replit secrets)
APP_ID = os.getenv('PINTEREST_APP_ID')
APP_SECRET = os.getenv('PINTEREST_APP_SECRET')
ACCESS_TOKEN = os.getenv('PINTEREST_ACCESS_TOKEN')
BOARD_ID = os.getenv('PINTEREST_BOARD_ID')
OPENAI_KEY = os.getenv('OPENAI_KEY')

client = OpenAI(api_key=OPENAI_KEY)

def generate_content(prompt):
    # Text
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Title and description for Pinterest pin: {prompt}"}]
    )
    lines = resp.choices[0].message.content.strip().split('\n')
    title = lines[0]
    desc = '\n'.join(lines[1:]) if len(lines) > 1 else ""

    # Image
    img = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", n=1)
    img_data = requests.get(img.data[0].url).content
    b64 = base64.b64encode(img_data).decode()
    return title, desc, b64

def create_pin(title, desc, b64_img, link):
    url = "https://api.pinterest.com/v5/pins"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "board_id": BOARD_ID,
        "title": title,
        "description": desc + f"\n{link}",
        "link": link,
        "media_source": {
            "source_type": "image_base64",
            "content_type": "image/jpeg",
            "data": b64_img
        }
    }
    r = requests.post(url, json=data, headers=headers)
    return r.json()

# Test
if __name__ == "__main__":
    prompt = input("Prompt: ")
    link = input("Affiliate link: ")
    t, d, img = generate_content(prompt)
    print(create_pin(t, d, img, link))
