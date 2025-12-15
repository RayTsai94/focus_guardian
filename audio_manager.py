import os
import threading
import subprocess
from gtts import gTTS

class AudioManager:
    def __init__(self, base_dir="."):
        self.output_dir = os.path.join(base_dir, "audio_cache")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _generate_mp3(self, text, filename):
        file_path = os.path.join(self.output_dir, filename)
        if os.path.exists(file_path):
            return file_path
        try:
            tts = gTTS(text=text, lang='en')
            tts.save(file_path)
            return file_path
        except Exception as e:
            print(f"gTTS Error: {e}")
            return None

    def _play_thread(self, text, cache_key):
        if not cache_key:
            cache_key = str(hash(text))
        filename = f"{cache_key}.mp3"
        
        mp3_path = self._generate_mp3(text, filename)
        
        if mp3_path:
            #audio played by mpg123
            
            cmd = f"mpg123 -q '{mp3_path}'"
            try:
                subprocess.run(cmd, shell=True, check=False)
            except Exception as e:
                print(f"Playback Error: {e}")

    def speak(self, text, cache_key=None):
        threading.Thread(target=self._play_thread, args=(text, cache_key)).start()

if __name__ == "__main__":
    AudioManager().speak("Audio system test passed", "test-en")
