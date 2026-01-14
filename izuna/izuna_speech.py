from RealtimeSTT import AudioToTextRecorder
import asyncio

#import sounddevice as sd
#print(sd.query_devices())


# Global variables
numberOfComments = 0
past_conversation_log = []
preferred_input_device = 1  # sounddevice input index
user = "User"

def speech_init():
    """
    Create and return an AudioToTextRecorder.
    MUST be called inside __main__ on Windows.
    """
    recorder = AudioToTextRecorder(input_device_index=preferred_input_device)
    return recorder


async def listen_once(recorder):
    """
    Async wrapper around the blocking recorder.text()
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, recorder.text)
