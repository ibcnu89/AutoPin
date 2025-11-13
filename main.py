import requests
import base64
from openai import OpenAI
import os
from PIL import Image
from io import BytesIO

# Load from environment (set in Replit secrets)
APP_ID = os.getenv('PINTEREST_APP_ID')
APP_SECRET = os.getenv('PINTEREST_APP_SECRET')
ACCESS_TOKEN = os.getenv('PINTEREST_ACCESS_TOKEN')
BOARD_ID = os.getenv('PINTEREST_BOARD_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_content(prompt):
    # Text
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Title and description for Pinterest pin: {prompt}"}]
    )
    lines = resp.choices[0].message.content.strip().split('\n')
    title = lines[0]
    desc = '\n'.join(lines[1:]) if len(lines) > 1 else ""

    # Image (DALL-E returns PNG, convert to JPEG for Pinterest)
    img = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", n=1)
    img_data = requests.get(img.data[0].url).content
    
    # Convert PNG to JPEG (normalize all modes to RGBA first)
    png_image = Image.open(BytesIO(img_data))
    
    # Normalize to RGBA to handle all PNG modes (RGB, RGBA, LA, P, etc.)
    if png_image.mode != 'RGBA':
        png_image = png_image.convert('RGBA')
    
    # Composite over white background (JPEG doesn't support transparency)
    rgb_image = Image.new('RGB', png_image.size, (255, 255, 255))
    rgb_image.paste(png_image, mask=png_image.split()[3])  # Use alpha channel as mask
    
    # Save as JPEG to bytes
    jpeg_buffer = BytesIO()
    rgb_image.save(jpeg_buffer, format='JPEG', quality=95)
    jpeg_data = jpeg_buffer.getvalue()
    
    b64 = base64.b64encode(jpeg_data).decode()
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
