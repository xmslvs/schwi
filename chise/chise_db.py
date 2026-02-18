import time
from urllib import response
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import aiosqlite
import asyncio
from .chise_groq import gen_groq_response

#Init ChromaDB client and collections for user data and input-response pairs

import chromadb
client = chromadb.PersistentClient(path="./chroma_storage")

col_chise_data = client.get_or_create_collection(
    name ="chise_data",
    metadata = {
        "description": "Persistent memory of all past user inputs.",
        "usecase": "Used in Chise model prompts to gather context of user information."
    }
    )

con = None
c = None
#TODO:: setup db for storing each unique user, as well as the number of times they have messaged, plus a summary of their info
async def init_user_db():
    con = await aiosqlite.connect("user_data.db")
    c = await con.cursor()
    await c.execute("CREATE TABLE IF NOT EXISTS user_data(user TEXT, msg_count INTEGER, summary TEXT, last_update INTEGER)")
    await con.commit()

asyncio.run(init_user_db())


emb_fn = SentenceTransformer("all-MiniLM-L6-v2")

async def add_user_msg_to_db(input, response):
    data = [input["response"]]

    col_chise_data.add(
        documents=data,
        embeddings=emb_fn.encode(data).tolist(),
        ids=[str(time.time_ns())],
        metadatas=[{"user" : str(input["user"]), "response": str(response), "datetime": time.time_ns()}]
    )
    # increment db user_msg_count (for tracking total number of messages sent by user, which can be used in prompts)
    global con, c
    if con is None:
        con = await aiosqlite.connect("user_data.db")
        c = await con.cursor()
    await c.execute("SELECT msg_count FROM user_data WHERE user = ?", (input["user"],))
    result = await c.fetchone()
    if result is not None:
        msg_count = result[0]
        await c.execute("UPDATE user_data SET msg_count = ? WHERE user = ?", (msg_count + 1, input["user"]))
    else:
        await c.execute("INSERT INTO user_data(user, msg_count, summary, last_update) VALUES (?, 1, '', 0)", (input["user"],))
    await con.commit()
    if result is not None and msg_count % 10 == 0:
        await update_user_summary(input, msg_count) # if user_msg_count % 10 == 0, update_user_summary() (update db summary of user information and last update datetime)

async def close_db():
    global con
    if con is not None:
        await con.close()


async def consistent_response_context(input):
    query = input
    query_vec = emb_fn.encode([query]).tolist()[0]

    results = col_chise_data.query(
        query_embeddings=[query_vec],
        n_results=5
    )
    responses = []
    for metadata in results["metadatas"]: # returns sairo's responses to the 5 most similar past user inputs
        if len(metadata) > 0:
            responses.append(metadata[0]["response"])
    return responses

async def update_user_summary(input, msg_count):
    # get summary_db last update datetime
    global con, c
    if con is None:
        con = await aiosqlite.connect("user_data.db")
        c = await con.cursor()
    await c.execute("SELECT last_update FROM user_data WHERE user = ?", (input["user"],))
    last_update = await c.fetchone()
    await c.execute("SELECT summary FROM user_data WHERE user = ?", (input["user"],))
    summary = await c.fetchone()
    results = col_chise_data.get(
        where={
            "$and": [
                {"user": input["user"]},
                {"datetime": {"$gt": last_update[0] if last_update else 0}},
            ]})
    user_info = results["documents"]
    prompt = await get_prompt(input, user_info, summary[0] if summary else "", msg_count)
    response = await gen_groq_response(prompt)
    if response["response"].find("\"response\": ") != -1:
        response_text = response["response"][response["response"].find("\"response\": ") + len("\"response\": "):response["response"].find("\"response_datetime\": ")]
    else:
        response_text = response["response"]
    await c.execute("UPDATE user_data SET summary = ?, last_update = ? WHERE user = ?", (response_text, time.time_ns(), input["user"]))
    await con.commit()

async def get_prompt(input, user_info, summary, msg_count):
    prompt = f"""
        The following is a list of recent messages sent from one user to Sairo, an livestreamer. 
        The user's name is {input["user"]}. The user has sent {msg_count} messages total so far.
        You have the following summary about the user so far: {summary}
        The user's recent messages are as follows: {user_info}
        Based on the user's recent messages, and the summary of the user's information, generate an updated summary of the user's information.
        The updated summary should be concise, and should only include information that can be inferred from the user's messages.
        The updated summary should be readable to another LLM, and should be in the format of a list of key-value pairs, where the key is a category of information (e.g. "hobbies", "personality traits", "relationship to Sairo", etc.) and the value is a brief summary of the user's information in that category.
        Always return the summary in the following JSON format:
        {{
            "hobbies": [brief summary of user's hobbies],
            "personality_traits": [brief summary of user's personality traits],
            "relationship_to_sairo": [brief summary of user's relationship to Sairo],
            "other_information": [brief summary of any other relevant information about the user]
        }}
    """ 
    return prompt

async def get_user_summary(user):
    global con, c
    if con is None:
        con = await aiosqlite.connect("user_data.db")
        c = await con.cursor()
    await c.execute("SELECT summary FROM user_data WHERE user = ?", (user,))
    summary = await c.fetchone()
    return summary[0] if summary else ""