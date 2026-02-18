import asyncio
import logging
from izuna import izuna_youtube
from chise import chise_groq, chise_db
from saya import saya_cli
from saya.saya_qwen3 import commit as saya_qwen
from multiprocessing import freeze_support
from izuna.izuna_screen_recognition import izuna_screen_to_text

async def screen_to_text(shared_state):
    while True:
        try:
            # Update the key inside the dictionary
            response = await izuna_screen_to_text.get_vlm_response()
            shared_state["screen_context"] = response
            logging.info("Screen information updated: %s", response[:20])
        except Exception as e:
            logging.error(f"Error getting VLM response: {e}")
        
        await asyncio.sleep(20)

past_conversation_log = []

async def main():
    YoutubeLink = input("Enter Youtube Live Stream Link: ")
    # 2. Create a shared state dictionary
    # This allows the background task to update "screen_context" 
    # and the main loop to read the NEW value immediately.
    shared_state = {"screen_context": "Initial screen context not yet available."}
    webdriver = izuna_youtube.youtube_init(YoutubeLink)

    # --- STT recorder must be created inside __main__ ---
    global _audio_stream
    _audio_stream = None
    tts_client = saya_qwen.saya_qwen_init()

    # Establish connection
    await tts_client.connect()
    # Execute message handling and user input in parallel
    consumer_task = asyncio.create_task(tts_client.handle_messages())
     # Start the screenshot cycle in the background
    asyncio.create_task(izuna_screen_to_text.screenshot_cycle())
    # start screen to text task in the background, passing the shared state dictionary
    asyncio.create_task(screen_to_text(shared_state))

    while True:
        try:
            # Listen for user input
            user_input = await asyncio.to_thread(izuna_youtube.youtube_input, webdriver)

            past_responses = await chise_db.consistent_response_context(user_input)
            user_summary = await chise_db.get_user_summary(user_input["user"])
            print("User Input:", user_input)
            past_conversation_log.append(user_input)
            current_screen_data = shared_state["screen_context"]
            if user_input != "":
                with open('stream_text\\input.txt', 'w') as fp:
                    fp.write(user_input["response"])
            else:
                with open('stream_text\\input.txt', 'w') as fp:
                    fp.write("(No user input detected)")

            # Generate model input
            gemini_input = chise_groq.system_prompt(user_input, past_conversation_log, current_screen_data, user_summary, past_responses)
            response = await chise_groq.gen_groq_response(gemini_input)

            asyncio.create_task(chise_db.add_user_msg_to_db(user_input, response))

            past_conversation_log.append(response)
            if response is None:
                print("Skipping response due to parsing error.")
                continue
            if response["response"].find("\"response\": ") != -1:
                response_text = response["response"][response["response"].find("\"response\": ") + len("\"response\": "):response["response"].find("\"response_datetime\": ")]
            else:
                response_text = response["response"]
            with open('stream_text\\output.txt', 'w') as fp:
                fp.write(response_text)

            await saya_qwen._user_input_sequence(tts_client, input_text=response_text)  # Wait for user input to complete
            # Wait for response.done
            await tts_client.wait_for_response_done()
            # Print and parse output
            # saya_cli.saya_cli(response)

            # Close connection and cancel consumer task
        except (KeyboardInterrupt, EOFError):
            logging.info("User requested exit, closing connection...")
            break
    consumer_task.cancel()
    saya_qwen.saya_qwen_close(tts_client)
    chise_db.close_db()


if __name__ == "__main__":
    freeze_support()  # ✅ MUST on Windows when using multiprocessing
    asyncio.run(main())
