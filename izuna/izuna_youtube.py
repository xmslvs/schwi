from selenium import webdriver 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import time
import random

#TODO: implement youtube live chat choose function
MINWAIT = 60 # minimum wait time for new comment
MAXWAIT = 61 # maximum wait time for new comment
YoutubeLink = "https://www.youtube.com/watch?v=5qap5aO4i9A" # default YouTube live stream link

def youtube_init(YoutubeLink):
    global numberOfComments
    driver = webdriver.Firefox()
    print("webdriver initialized")
    driver.get(YoutubeLink)
    print("YouTube link get")
    initialWait = WebDriverWait(driver, 60)
    print("webdriver waited")
    commentsContainer = initialWait.until(expected_conditions.presence_of_element_located([By.CSS_SELECTOR, "div[id^=items]"]))
    print("comment container found")
    if commentsContainer == None:
        print("ERROR: cannot find comments container")
    time.sleep(1)
    numberOfComments = len(commentsContainer.find_elements(By.CSS_SELECTOR, "yt-live-chat-text-message-renderer"))
    print("comments so far (ignoring): " + str(numberOfComments))
    return driver


def youtube_input(driver):
    global numberOfComments
    newCommentText = "div[id^=items] > :nth-child(" + str(numberOfComments) + " of yt-live-chat-text-message-renderer) > div[id^=content] > span[id^=message]"
    newCommentAuthor = "div[id^=items] > :nth-child(" + str(numberOfComments) + " of yt-live-chat-text-message-renderer) > div[id^=content] > yt-live-chat-author-chip > span[id^=author-name]"
    print("waiting for up to " + str(MAXWAIT) + " seconds for a new comment...")
    
    for i in range(0, random.randint(MINWAIT, MAXWAIT)): # wait for a new comment to appear
        new_comment = driver.find_elements(By.CSS_SELECTOR, newCommentText)
        if (len(new_comment) == 0): # no new comment found, waiting...
            time.sleep(1)
        else:
            newCommentTextData = (WebDriverWait(driver, 1)).until(expected_conditions.visibility_of_element_located([By.CSS_SELECTOR, newCommentText]))
            newCommentAuthorData = (WebDriverWait(driver, 1)).until(expected_conditions.visibility_of_element_located([By.CSS_SELECTOR, newCommentAuthor]))
            print("new comment found")
            numberOfComments += 1
            print(newCommentAuthorData.text + ": " + newCommentTextData.text)  #prints current user's comment
            newCommentData = {
                "user": newCommentAuthorData.text, 
                "response": newCommentTextData.text, 
                "response_datetime": time.time_ns()
                }
            return newCommentData
    print("no new comment found after waiting")
    newCommentData = {
                "user": "", 
                "response": "", 
                "response_datetime": time.time_ns()
                }
    return newCommentData
    

