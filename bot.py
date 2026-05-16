import os
import asyncio
import google.generativeai as genai
import edge_tts
import subprocess

# Put your exact API key right between these quotes
MY_KEY = "AIzaSyBbPQSK2cre-seslNxhrRw7Wf973C7hIWo"

# We configure the key directly using a clean method
genai.configure(api_key=MY_KEY)

# Use 'gemini-pro' since it matches this specific package version
model = genai.GenerativeModel('gemini-pro') 

try:
    response = model.generate_content("Write a 30-second fascinating and bizarre historical fact for a Facebook Reel. Do not include any stage directions or visual cues, just the spoken text.")
    script_text = response.text.replace('*', '')
    print("Script Generated successfully!")
except Exception as e:
    print(f"Google Gemini Error: {e}")
    script_text = "The Titanic was an incredibly massive ship, but did you know its whistles could be heard eleven miles away?"

# 2. Generate the AI Voiceover
async def generate_audio():
    communicate = edge_tts.Communicate(script_text, "en-US-ChristopherNeural")
    await communicate.save("voice.mp3")

asyncio.run(generate_audio())
print("Audio Generated!")

# 3. Find your background video file
mp4_files = [f for f in os.listdir('.') if f.endswith('.mp4') and f != 'output.mp4']
if not mp4_files:
    print("Error: No background video file found in the repository!")
    exit(1)
bg_video = mp4_files[0] 

# 4. Stitch the Audio and Video together using FFmpeg
print(f"Stitching video together using background: {bg_video}")
subprocess.run([
    'ffmpeg', '-y', '-stream_loop', '-1', '-i', bg_video, '-i', 'voice.mp3',
    '-c:v', 'libx264', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
    '-shortest', 'output.mp4'
])
print("Video created successfully!")
