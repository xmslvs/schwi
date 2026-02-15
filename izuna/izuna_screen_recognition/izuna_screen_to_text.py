from groq import AsyncGroq
import base64
import asyncio
import os
from .izuna_screencapture import take_screenshot, update_screen_history, take_screenshot


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

async def screenshot_cycle():
   take_screenshot()
   while True:
        update_screen_history()
        await asyncio.sleep(2)

client = AsyncGroq(api_key=os.environ.get("groq_vlm_key"))

async def get_vlm_response():
    image_path_0 = "screen_context\\screen_0.png"
    image_path_1 = "screen_context\\screen_1.png"  
    image_path_2 = "screen_context\\screen_2.png"

    # Getting the base64 string
    base64_image_0 = encode_image(image_path_0)
    base64_image_1 = encode_image(image_path_1)
    base64_image_2 = encode_image(image_path_2) 

    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                {"type": "text", "text": "The following are a list of screenshots from a computer display, taken 2 seconds apart. The first image is the most recent image. Carefully explain, in detail, the current state of the on-screen content, and how it has changed recently. If you see an animated or cartoon character with white hair, it is likely that the character is called Sairo, so refer to her as such."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image_0}",
                        },
                    },
                                        {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image_1}",
                        },
                    },
                                        {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image_2}",
                        },
                    },
                ],
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )
    # print("VLM response generated: " + chat_completion.choices[0].message.content)
    return(chat_completion.choices[0].message.content)

