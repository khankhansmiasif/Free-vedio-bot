import os
import asyncio
import google.generativeai as genai
import edge_tts
import subprocess

# 1. Setup Gemini AI to write the script
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') 
response = model.generate_content("Write a 30-second fascinating and bizarre historical fact for a Facebook Reel. Do not include any stage directions or visual cues, just the spoken text.")
script_text = response.text.replace('*', '')

print("Script Generated:", script_text)

# 2. Generate the AI Voiceover
async def generate_audio():
    communicate = edge_tts.Communicate(script_text, "en-US-ChristopherNeural")
    await communicate.save("voice.mp3")

asyncio.run(generate_audio())
print("Audio Generated!")

# 3. Find the video you uploaded
mp4_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
bg_video = mp4_files[0] 

# 4. Stitch the Audio and Video together using FFmpeg
print("Stitching video together...")
subprocess.run([
    'ffmpeg', '-stream_loop', '-1', '-i', bg_video, '-i', 'voice.mp3',
    '-c:v', 'libx264', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
    '-shortest', 'output.mp4'
])
print("Video created successfully!")
