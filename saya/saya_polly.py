from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import io
import tempfile

import time
import asyncio
# Import pygame modules lazily inside functions to avoid welcoming message during imports and
# to defer device and mixer initialization until actually needed.


# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="my-dev-profile")
polly = session.client("polly")
current_dir = os.getcwd()
# Initialize mixer lazily via helper to avoid multiple init calls and redundant messages
from audio_utils import ensure_mixer_initialized
# Optionally choose a device here when needed; we initialize right before playback to avoid conflicts
# ensure_mixer_initialized(devicename='3.5mm Output (Realtek(R) Audio)')


async def speak_polly_response(input):
    try:
        # Request speech synthesis
        response = polly.synthesize_speech(Text=input, OutputFormat="mp3",
                                            VoiceId="Ivy")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Read the whole stream into memory so we get a seekable buffer
        with closing(response["AudioStream"]) as stream:
            audio_bytes = stream.read()

        # Ensure mixer is initialized (do this lazily to avoid repeated init messages)
        ensure_mixer_initialized()

        # Import mixer when needed
        from pygame import mixer

        buf = io.BytesIO(audio_bytes)
        buf.seek(0)

        temp_filename = None
        try:
            # pygame may require a seekable file-like object; BytesIO should work,
            # but if it fails (different SDL builds), fall back to a temp file.
            mixer.music.load(buf)
        except Exception as e:
            print("Direct load from BytesIO failed, falling back to temp file:\n", e)
            # write to a temporary file and load that instead
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            try:
                tf.write(audio_bytes)
                tf.flush()
                temp_filename = tf.name
            finally:
                tf.close()
            mixer.music.load(temp_filename)

        mixer.music.play()
        # wait for playback to finish
        while mixer.music.get_busy():
            time.sleep(0.1)

        # Clean up
        try:
            mixer.music.unload()
        except Exception:
            pass
        if temp_filename:
            try:
                os.remove(temp_filename)
            except Exception:
                pass
    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)

    # # Play the audio using the platform's default player
    # if sys.platform == "win32":
    #     os.startfile(output)
    # else:
    #     # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
    #     opener = "open" if sys.platform == "darwin" else "xdg-open"
    #     subprocess.call([opener, output])


    # mixer.init() # Initialize the mixer, this will allow the next command to work

    # # Returns playback devices, Boolean value determines whether they are Input or Output devices.
    # print("Inputs:", devicer.audio.get_audio_device_names(True))
    # print("Outputs:", devicer.audio.get_audio_device_names(False))

    # mixer.quit() # Quit the mixer as it's initialized on your main playback device

    # # Moved to top of file
    # mixer.init(devicename = 'CABLE-C Input (VB-Audio Cable C)') # Initialize it with the correct device

    # mixer.music.load("polly_output.mp3") # Load the mp3
    # mixer.music.play() # Play it

    # while mixer.music.get_busy():  # wait for music to finish playing
    #     time.sleep(1)
    # mixer.music.unload() # Unload the mp3
    # os.remove(output)
    return