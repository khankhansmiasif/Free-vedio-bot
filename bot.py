import os
import asyncio
import google.generativeai as genai
import edge_tts
import subprocess
import requests

# 1. Setup Gemini AI securely using GitHub Secrets
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Warning: GEMINI_API_KEY secret not found. Using backup script.")
    script_text = "The Titanic was an incredibly massive ship, but did you know its whistles could be heard eleven miles away?"
else:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro') 
        prompt = (
            "Write a 30-second fascinating and bizarre historical fact for a Facebook Reel. "
            "Do not include any stage directions, intro/outro text, or visual cues. Just provide the raw spoken text."
        )
        response = model.generate_content(prompt)
        script_text = response.text.replace('*', '').strip()
        print("Script Generated successfully!")
    except Exception as e:
        print(f"Google Gemini Error: {e}")
        script_text = "The Titanic was an incredibly massive ship, but did you know its whistles could be heard eleven miles away?"

print(f"Final Script Content: {script_text}")

# 2. Generate the AI Voiceover
async def generate_audio():
    communicate = edge_tts.Communicate(script_text, "en-US-ChristopherNeural")
    await communicate.save("voice.mp3")

asyncio.run(generate_audio())
print("Audio Voiceover Generated!")

# 3. Find your uploaded template video
mp4_files = [f for f in os.listdir('.') if f.endswith('.mp4') and f != 'output.mp4']
if not mp4_files:
    print("Error: No background template video (.mp4) found in your repository!")
    exit(1)
bg_video = mp4_files[0] 

# 4. Stitch the Audio and Template Video together using FFmpeg
print(f"Stitching video together using template: {bg_video}")
subprocess.run([
    'ffmpeg', '-y', '-stream_loop', '-1', '-i', bg_video, '-i', 'voice.mp3',
    '-c:v', 'libx264', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
    '-shortest', 'output.mp4'
])
print("Output video created successfully!")

# 5. Send the finished Reel to your Make.com Webhook
webhook_url = "https://hook.eu1.make.com/8n94ewck1pinuuvbeg3t7qpsqqnmva2t"
print("Uploading final video to Make.com...")

try:
    with open("output.mp4", "rb") as video_file:
        files = {"file": ("output.mp4", video_file, "video/mp4")}
        # Also sending the generated script text so you can use it as a caption in Make!
        data = {"caption": script_text}
        
        response = requests.post(webhook_url, files=files, data=data)
        
    if response.status_code == 200:
        print("Successfully sent to Make.com!")
    else:
        print(f"Failed to send to Make. Server responded with code: {response.status_code}")
except Exception as e:
    print(f"Error transferring file to Webhook: {e}")
