import os
import asyncio
import logging
import wave
from .tts_realtime_client import TTSRealtimeClient, SessionMode
import pyaudio
from dotenv import load_dotenv
load_dotenv()

# QwenTTS service configuration
# Replace model with qwen3-tts-instruct-flash-realtime and uncomment instructions in tts_realtime_client.py to use instruction control
# Singapore region URL. Replace with wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen3-tts-flash-realtime for Beijing region models
URL = "wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime?model=qwen3-tts-instruct-flash-realtime"
# API Keys differ between Singapore and Beijing regions. Get your API Key: https://www.alibabacloud.com/help/zh/model-studio/get-api-key
# Replace with your Model Studio API Key if environment variable is not configured: API_KEY="sk-xxx"
API_KEY = os.getenv("qwen_key")

if not API_KEY:
    raise ValueError("Please set qwen_key environment variable")

# Collect audio data
_audio_chunks = []
_AUDIO_SAMPLE_RATE = 24000
_audio_pyaudio = pyaudio.PyAudio()
_audio_stream = None

def _audio_callback(audio_bytes: bytes):
    """TTSRealtimeClient audio callback: play and cache in real time"""
    global _audio_stream
    if _audio_stream is not None:
        try:
            _audio_stream.write(audio_bytes)
        except Exception as exc:
            logging.error(f"PyAudio playback error: {exc}")
    _audio_chunks.append(audio_bytes)
    logging.info(f"Received audio chunk: {len(audio_bytes)} bytes")

def _save_audio_to_file(filename: str = "output.wav", sample_rate: int = 24000) -> bool:
    """Save collected audio data to WAV file"""
    if not _audio_chunks:
        logging.warning("No audio data to save")
        return False

    try:
        audio_data = b"".join(_audio_chunks)
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
        logging.info(f"Audio saved to: {filename}")
        return True
    except Exception as exc:
        logging.error(f"Failed to save audio: {exc}")
        return False

async def _user_input_sequence(client: TTSRealtimeClient, input_text: str):
    # """Continuously get user input and send text. When user enters empty text, send commit event and end current session"""
    """Continuously get user input and send text, comitting and returning audio. Ignore empty input"""
    if not input_text:  # User entered empty input
        logging.info("Empty input, ignoring")
    else:
        logging.info(f"Sending text: {input_text}")
        await client.append_text(input_text)
        await client.commit_text_buffer()
        await asyncio.sleep(0.4)
            
    

# End session
logging.info("Ending session...")
async def _run_demo():
    """Run complete demo"""
    global _audio_stream
    # Open PyAudio output stream
    _audio_stream = _audio_pyaudio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=_AUDIO_SAMPLE_RATE,
        output=True,
        frames_per_buffer=1024
    )

    client = TTSRealtimeClient(
        base_url=URL,
        api_key=API_KEY,
        voice="Bella",
        mode=SessionMode.COMMIT,  # Change to COMMIT mode
        audio_callback=_audio_callback
    )

    # Establish connection
    await client.connect()
    # Execute message handling and user input in parallel
    consumer_task = asyncio.create_task(client.handle_messages())
    while(True):
        try:
            producer_task = asyncio.create_task(_user_input_sequence(client, input_text=input("> ")))
            await producer_task  # Wait for user input to complete

            await asyncio.sleep(3)  # Ensure all audio is received before closing stream
            # Wait for response.done
            await client.wait_for_response_done()

            # Close connection and cancel consumer task
        except (KeyboardInterrupt, EOFError):
            logging.info("User requested exit, closing connection...")
            break
    await client.finish_session()
    await client.close()
    consumer_task.cancel()
    
        

    # Close audio stream
    if _audio_stream is not None:
        _audio_stream.stop_stream()
        _audio_stream.close()
    _audio_pyaudio.terminate()

    # Save audio data
    os.makedirs("outputs", exist_ok=True)
    # _save_audio_to_file(os.path.join("outputs", "qwen_tts_output.wav"))
    



def saya_qwen_init() -> TTSRealtimeClient:
    logging.info("Starting QwenTTS Realtime Client demo…")
    
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
            print("Output Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
    output_index = int(input("Select output device index: "))

    global _audio_stream
    # Open PyAudio output stream
    _audio_stream = _audio_pyaudio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=_AUDIO_SAMPLE_RATE,
        output=True,
        frames_per_buffer=1024,
        output_device_index=output_index
    )

    client = TTSRealtimeClient(
        base_url=URL,
        api_key=API_KEY,
        voice="Bella",
        mode=SessionMode.COMMIT,  # Change to COMMIT mode
        audio_callback=_audio_callback
    )
    return client

async def saya_qwen_close(client: TTSRealtimeClient):
    await client.finish_session()
    await client.close()

    # Close audio stream
    if _audio_stream is not None:
        _audio_stream.stop_stream()
        _audio_stream.close()
    _audio_pyaudio.terminate()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Starting QwenTTS Realtime Client demo…")
    asyncio.run(_run_demo())

if __name__ == "__main__":
    main() 