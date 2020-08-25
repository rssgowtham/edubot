from django.shortcuts import render

# Create your views here.

from twilio.twiml.messaging_response import Media, Message, MessagingResponse
from twilio.rest import Client
from django.http import HttpResponse
import pdfkit
from googletrans import Translator
from .audiototext import convertAudioToText, formatAudio
from .ImageToText import convertImageToText, formatImage
from .databaseAPI import *
from .getlinks import getDifferentLinks
from .deletefiles import deleteFiles
import time
import requests
# from .models import User

precautions = "Please follow these precautions\n\n1. Image should be taken at good light.\n2. Try to allocate some empty space around the text.\n3. Make sure the text is visible clearly.\n4. crop the unnecessary images."

acc_sid = "AC8f54df63e512926d1b3794247870066f"
auth_token = "633b3de30ea428f966ec2bcf4277afb0"

domain = "http://655cf9e74661.ngrok.io/"


def translate(text, language):
    translator = Translator()
    translated = translator.translate(text, dest=language)
    return translated.text


def getId(req):
    return req.POST['MessageSid']


def getNum(req):
    return req.POST['From']


def sendMsg(user_number, msg):
    print("sended msg", msg)
    client = Client(acc_sid, auth_token)
    from_w = 'whatsapp:+14155238886'
    to_ = user_number
    message = client.messages.create(body=msg,from_=from_w, to=to_)


def sendPdf(user_number, pdf, name):
    sendMsg(user_number, "We are sending "+ name + " pdf\n\nPlease wait . . .")
    client = Client(acc_sid, auth_token)
    from_w = 'whatsapp:+14155238886'
    to_ = user_number
    print(domain + pdf)
    message = client.messages.create(media_url=[domain + pdf], body=name,from_=from_w, to=to_)

def extractPdf(pdf_link, pdf_path):
    myfile = requests.get(pdf_link)
    open(pdf_path, 'wb').write(myfile.content)

def createAndSendPdf(user_number, msg_id, links_data, pdf_link, pdf_title, nth_pdf):
    pdf_path = "media/" + str(msg_id) + str(nth_pdf) + ".pdf"
    try:
        if(pdf_title[:5].lower() == "[pdf]"):
            extractPdf(pdf_link, pdf_path)
        else:
            pdfkit.from_url(pdf_link, pdf_path)
        print("pdf done")
    except:
        print("pdf not done")
    finally:
        sendMsg(user_number, links_data)
        sendPdf(user_number, pdf_path, pdf_title)
        print("pdf sent")


def prepareToSendPdfs(user_number, msg_id, links_data, pdf_links, pdf_titles):
    for i in range(len(links_data)):
        createAndSendPdf(user_number,msg_id, links_data[i], pdf_links[i], pdf_titles[i], i)

LANGUAGECODES = ['te', "ur", "hi", "ta", "pa", "es", "ne", "mr", "ml", "ko", "kn", "ja", "it", "gu", "de", "fr", "zh-cn", "bn"]
LANGUAGES = ["Telugu","Urdu", "Hindi", "Tamil", "Punjabi", "Spanish", "Nepali", "Marathi", "Malayalam", "Korean", "Kannada", "Japanese",
             "italian", "Gujarati", "German", "French", "Chinese", "Bengali"]
def sendSelectLanguageMsg(user_number):
    langs = [ str(i+1)+"."+LANGUAGES[i]+"\n" for i in range(len(LANGUAGES))]
    sendMsg(user_number, "select language to translate\n" + ''.join(langs))


def sendWantDataMsg(user_number, service):
    sendMsg(user_number, "Send any one: Image, audio, and Text to enjoy " + service + " Service")


def sendSelectServiceMsg(user_number):
    sendMsg(user_number, "select service to continue...\n1.search\n2.translate")

def sendSelectLanguageOrServiceMsg(user_number):
    sendMsg(user_number, "select option\n1.Change language\n2.Change Service\n")

def sendWantToContinueWithOldDataMsg(user_number,search_query):
    sendMsg(user_number, "Do you want to continue with the existing data::\n\"" + search_query + "\"\n\n1.Yes\n2.No")
    updateUseOldData(user_number, True)

def processTranslate(user_number, text_list):
    updateRequireService(number=user_number, requireService=False)
    language = getLanguage(user_number)

    if not language or isRequireLanguage(user_number):
        updateRequireLanguage(number=user_number, requireLanguage=True)
        sendSelectLanguageMsg(user_number)
        updateSearchQuery(number=user_number, searchQuery="\n".join(text_list))
        return
    # updateLanguage(user_number, None)
    for text in text_list:
        meaning = text + " = " + translate(text, language)
        sendMsg(user_number, meaning)
    updateChangeLanguageOrService(number=user_number, changeLanguageOrService=True)
    sendSelectLanguageOrServiceMsg(user_number)
    sendMsg(user_number,"if u want to change language or service....\notherwise continue in translate mode")

def processSearch(req, user_number, text_list):
    no_of_responses = 0
    try:
        # sendMsg(user_number, text_list)
        links_data, pdf_links, pdf_titles = getDifferentLinks(text_list)
        no_of_responses = len(links_data)
        if no_of_responses == 0:
            error = "text is empty"
            sendMsg(user_number, error)
            return
        prepareToSendPdfs(user_number, getId(req), links_data, pdf_links, pdf_titles)

    except Exception as e:
        error_msg = str(e)
        sendMsg(user_number, error_msg)
    finally:
        updateRequireService(number=user_number, requireService=True)
        sendSelectServiceMsg(user_number)
        sendMsg(user_number,"if u want to change service....\notherwise continue in search mode")


def getTextFromRequest(req):
    text_list = ""
    try:
        msg_id = getId(req)
        user_number = getNum(req)
        if req.POST['NumMedia'] == '1':
            media_url = req.POST['MediaUrl0']
            type_of_msg = req.POST['MediaContentType0']
            if type_of_msg == "audio/ogg":
                filename = formatAudio(media_url,msg_id)
                sendMsg(user_number, "We checked your audio")
                text_list = convertAudioToText(filename)
            elif type_of_msg == "image/jpeg":
                img_path = formatImage(media_url, msg_id)
                sendMsg(user_number, "We got your Image!")
                east_path = "frozen_east_text_detection.pb"
                text_list = convertImageToText(img_path, east_path)
        else:
            text_list = req.POST['Body']
            print("textlist::", text_list)
            text_list = text_list.split("\n")
            text_list = [i for i in text_list if i.strip()]
    except:
        text_list = ""
    return text_list


def convertToService(msg):
    if msg == "1" or msg == 1:
        return "search"
    elif msg == "2" or msg == 2:
        return "translate"
    else:
        return False


def convertToLanguage(msg):

    if len(LANGUAGECODES) >= int(msg):
        return LANGUAGECODES[int(msg)-1]
    return False


def processService(req, user_number, msg):

    search_query = getSearchQuery(user_number)
    if isChangeLanguageOrService(user_number):
        updateChangeLanguageOrService(number=user_number, changeLanguageOrService=False)
        if msg == "1" or msg == 1 or msg == "one":
            updateRequireLanguage(number=user_number, requireLanguage=True)
            updateRequireService(number=user_number,requireService=False)
            sendSelectLanguageMsg(user_number)
        else:
            sendSelectServiceMsg(user_number)
            updateRequireService(number=user_number, requireService=True)
        return

    if isRequireLanguage(user_number):
        language = convertToLanguage(msg)
        if not language:
            sendSelectLanguageMsg(user_number)
            return
        updateLanguage(number=user_number, language=language)
        sendMsg(user_number, "Your language is set to " + LANGUAGES[int(msg)-1])
        updateRequireLanguage(number=user_number, requireLanguage=False)
        if not search_query:
            sendWantDataMsg(user_number, "translate")
        else:
            sendWantToContinueWithOldDataMsg(user_number,search_query)
            updateUseOldData(user_number,True)
        return
    if getUseOldData(user_number):
        updateUseOldData(number=user_number, requireUseOldData=False)
        service = getService(user_number)
        if not service:
            sendSelectServiceMsg(user_number)
            return
        if msg == "1":
            sendMsg(user_number,"contiinuing with old data")
            if service == "search":
                processSearch(req, user_number, search_query.split('\n'))
            elif service == "translate":
                processTranslate(user_number, search_query.split("\n"))
            return
        elif msg == "2":
            updateSearchQuery(user_number, searchQuery=None)
            sendWantDataMsg(user_number, service)
            return
        else:
            sendMsg(user_number,"Pls reply with 1 or 2\n1.if u want to continue with old data\n2.I will provide new data")
            return
    service = convertToService(msg)
    if not service:  # if option is not one or two
        sendSelectServiceMsg(user_number)
        return
    if not existingUser(user_number):
        addUser(number=user_number, service=service)
    else:
        updateService(number=user_number, service=service)
    sendMsg(user_number, "You are now in " + service + " mode")

    if not search_query:
        sendWantDataMsg(user_number, service)
        return False
    sendWantToContinueWithOldDataMsg(user_number,search_query)


def processData(req, user_number, text_list):
    service = getService(user_number) if existingUser(user_number) else ""
    print("service:::", service)
    if not service:
        if not existingUser(user_number):
            addUser(number=user_number, searchQuery="\n".join(text_list))
        else:
            updateSearchQuery(number=user_number, searchQuery="\n".join(text_list))
        sendSelectServiceMsg(user_number)
        return
    updateSearchQuery(user_number,'\n'.join(text_list))
    if service == "search":
        processSearch(req, user_number, text_list)
        return
    processTranslate(user_number, text_list)


def isServiceRequest(message):
    numbers = [str(i) for i in range(1,21)]
    numberWords = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine","ten","eleven"
                   "twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen","twenty"]
    if message in numbers:
        return message
    if message in numberWords:
        return str(numberWords.index(message) + 1)
    if message in ["yes", "no"]:
        return message
    else:
        False


def processRequest(req,user_number):
    text_list = getTextFromRequest(req)
    if text_list == "" or not text_list:
        sendMsg(user_number, "No text detected")
        return
    msg = isServiceRequest(str.lower(text_list[0])) if len(text_list) == 1 else False
    print("msg::", msg, " -- text::", text_list)
    if msg:
        processService(req, user_number, msg)
    else:
        processData(req, user_number, text_list)


def apifun(req):
    msg = Message()
    msg_resp = MessagingResponse()
    user_number = getNum(req)
    # User.objects.all().delete()
    # sendMsg(user_number, "Welcome to our project")
    processRequest(req, user_number)
    # text_list = getTextFromRequest(req)
    # type_of_msg, msg_id, no_of_responses = processSearch(req, user_number, text_list)
    # processTranslate(user_number, text_list)
    # msg.body(None)
    # msg_resp.append(msg)
    # return HttpResponse(msg_resp)
    time.sleep(10)
    deleteFiles(getId(req))
    return HttpResponse()
