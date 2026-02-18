# SAIRO
SAIRO (Scaled Artificial Identity Recognition Operation) is a project which aims to create an identity, Sairo/沙彩, who feels "real". Different from other AI chatbots, SAIRO does not seek to create characters which are helpful assistants, or romantic manipulators. Rather, SAIRO aims to create a character which "exists" as much as you or I do, in the collective mind. Taking inspriation from examples such as Lain (Serial Experiments Lain), Hatsune Miku (Crypton Future Media), and Virtual YouTubers, SAIRO aims to create a similar identity, but **without the need for human operation**. 

# SCHWI
SCHWI (Simulated Computer-Human Working Instance) is a part of SAIRO which aims to create an interactive character which can communicate one-to-one with people at scale, bypassing the limits of one-to-many human operation (VTubers) or prefabricated content (Lain, Miku), while maintaining a common identity, such that any two experiences with SCHWI can feel like talking to "the same person". 
Within SCHWI, the repository is separated into three parts:
- IZUNA (Input/Zero-User Network Apparatus):  
  IZUNA is the frontend input system through which information is passed further along the pipeline. Current input systems include YouTube livestream comments, Twitch integration, as well as speech recognition, as well as zero-user (independent) prompting.
- CHISE (Computer-Human Interactive Sentience Engine)  
  CHISE is the system which controls SCHWI's responses. Utilizing LLMs alongside short-term and long-term memory databases, current implementation utilizes Google Gemini for low-cost operation with limited resources (Free API). 
- SAYA (Synthetic Action-Yielding Agent)  
  SAYA is the frontend output system through which text/audio/motion/expressions are shown to the user. Current output systems include text, speech (through Amazon Polly), and VTube Studio API expression output, with plans for implementing 3D motion data.
TL;DR: IZUNA is the input system, CHISE is the brain, SAYA is the output system.
By combining the available programs in each part of SCHWI, it is possible to customize your pipeline for your own needs, such as text-to-text, text-to-speech, speech-to-speech, speech-to-speech+expression. This structure also makes it easier to upgrade CHISE while maintaining compatiblity for all input/output systems developed. 

# Technical Notes
## IZUNA
IZUNA is capable of passing in input from the microphone, the command line, as well as YouTube comments.
IZUNA also includes izuna_screen_recognition, which is for passing in information on-screen for the character to have as context.
The default configuration passes through the username, message content, and message time through to CHISE as a dict.
Additional data is passed through if necessary, such as screen data, user information, or past responses.


## CHISE
CHISE includes options to generate respones with both the Gemini and Groq API, although the Gemini version is currently deprecated and not up-to-date.
In order to reduce latency, the response generation is one-shotted through an LLM. The prompt is key in changing the response/personality traits of the character, meaning that this is where you likely want to change in order to configure your character.
CHISE also includes a chise_db.py, which manages both a ChromaDB vector database which stores input/response pairs as embeddings (to search semantically similar messages), as well as a SQLite database which contains user information which is periodically updated. 


## SAYA
SAYA is capable of speech output (through either AWS Polly or Alibaba Cloud Qwen3TTS), or text output through the CLI. 

# Instructions
## Execution
This repository is not at the stage of easy use yet: We are planning on simplifying and streamlining the UX for setting everything up, though priority right now remains on developing new features. 
The main runfile which is under development currently is youtube_to_qwen.py, which takes in YouTube comments from a livestream, and responds as audio to the comments. The program also writes the input and response separately to files in stream_text/, which can be used in OBS as text overlays. The audio can be piped through to OBS using external VACs such as VB-Audio-Cable. Integration with the VTube Studio API in order to change expressions and animations is planned, and under development. 