import asyncio
import logging
from izuna import izuna_speech
from chise import chise_groq
from saya import saya_cli
from saya.saya_qwen3 import commit as saya_qwen
from multiprocessing import freeze_support

past_conversation_log = []

async def main():
    # --- STT recorder must be created inside __main__ ---
    recorder = izuna_speech.speech_init()
    global _audio_stream
    _audio_stream = None
    tts_client = saya_qwen.saya_qwen_init()

    # Establish connection
    await tts_client.connect()
    # Execute message handling and user input in parallel
    consumer_task = asyncio.create_task(tts_client.handle_messages())

    while True:
        try:
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
            await saya_qwen._user_input_sequence(tts_client, input_text=response["response"][response["response"].find("\"response\": ") + 12:response["response"].find("\\n\"response_datetime\": ")])  # Wait for user input to complete
            # Wait for response.done
            await tts_client.wait_for_response_done()
            # Print and parse output
            saya_cli.saya_cli(response)

            # Close connection and cancel consumer task
        except (KeyboardInterrupt, EOFError):
            logging.info("User requested exit, closing connection...")
            break
    consumer_task.cancel()
    saya_qwen.saya_qwen_close(tts_client)


if __name__ == "__main__":
    freeze_support()  # ✅ MUST on Windows when using multiprocessing
    asyncio.run(main())
