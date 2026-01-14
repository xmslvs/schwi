import time

def cli_input():
    user = input("User name: ")
    response = input("Comment: ")
    newCommentData = {"user": user, "response": response, "response_datetime": time.ctime()}
    return newCommentData