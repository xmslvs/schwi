import asyncio
import json
from izuna import izuna_speech
from chise import chise_groq
from saya import saya_cli, saya_polly
from multiprocessing import freeze_support

past_conversation_log = []

async def main():
    # --- STT recorder must be created inside __main__ ---
    recorder = izuna_speech.speech_init()

    while True:
        # Listen for user input
        user_input = await izuna_speech.listen_once(recorder)
        print("User Input:", user_input)
        past_conversation_log.append(user_input)

        # Generate model input
        gemini_input = chise_groq.system_prompt(user_input, past_conversation_log)
        response = await chise_groq.gen_groq_response(gemini_input)

        past_conversation_log.append(response)
        if response is None:
            print("Skipping response due to parsing error.")
            continue

        # Print and parse output
        saya_cli.saya_cli(response)
        # Speak the response
        await saya_polly.speak_polly_response(response["response"])


if __name__ == "__main__":
    freeze_support()  # ✅ MUST on Windows when using multiprocessing
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting on user interrupt.")
