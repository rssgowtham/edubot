from .models import User


def addUser(number, service=None, language=None, searchQuery=None, requireLanguage=False, changeLanguageOrService=False,requireService= True):
    User(number=number, service=service, language=language, searchQuery=searchQuery,requireLanguage=requireLanguage,changeLanguageOrService=changeLanguageOrService,requireService=requireService).save()


def existingUser(number):
    if User.objects.filter(number=number).__len__() == 0:
        return False
    return True


def getUseOldData(number):
    if existingUser(number):
        user = User.objects.filter(number=number).values('number', 'requireUseOldData')
        return user[0]['requireUseOldData']
    return False


def updateUseOldData(number, requireUseOldData):
    if existingUser(number):
        User.objects.filter(number=number).update(requireUseOldData=requireUseOldData)
        return
    addUser(number=number, requireUseOldData=requireUseOldData)


def isRequireService(number):
    if existingUser(number):
        user = User.objects.filter(number=number).values('number', 'requireService')
        return user[0]['requireService']
    return False


def updateRequireService(number, requireService):
    if existingUser(number):
        User.objects.filter(number=number).update(requireService=requireService)
        return
    addUser(number=number, requireService=requireService)



def isChangeLanguageOrService(number):
    if existingUser(number):
        user = User.objects.filter(number=number).values('number', 'changeLanguageOrService')
        return user[0]['changeLanguageOrService']
    return False


def updateChangeLanguageOrService(number, changeLanguageOrService):
    if existingUser(number):
        User.objects.filter(number=number).update(changeLanguageOrService=changeLanguageOrService)
        return
    addUser(number=number, changeLanguageOrService=changeLanguageOrService)


def isRequireLanguage(number):
    if existingUser(number):
        user = User.objects.filter(number=number).values('number', 'requireLanguage')
        return user[0]['requireLanguage']
    return False


def updateRequireLanguage(number, requireLanguage):
    if existingUser(number):
        User.objects.filter(number=number).update(requireLanguage=requireLanguage)
        return
    addUser(number=number,service="translate", requireLanguage=requireLanguage)


def getService(number):
    if existingUser(number=number):
        user = User.objects.filter(number=number).values('number', 'service')
        return user[0]['service']
    else:
        return False

def updateService(number, service):
    if existingUser(number):
        User.objects.filter(number=number).update(service=service)
        return
    addUser(number=number, service=service)


def getLanguage(number):
    if existingUser(number=number):
        user = User.objects.filter(number=number).values('number', 'language')
        return user[0]['language']
    else:
        return None


def updateLanguage(number, language):
    if existingUser(number):
        User.objects.filter(number=number).update(language=language)
        return
    addUser(number=number, language=language)


def getSearchQuery(number):
    if existingUser(number):
        user = User.objects.filter(number=number).values('number', 'searchQuery')
        return user[0]['searchQuery']
    return ""


def updateSearchQuery(number,searchQuery):
    if existingUser(number):
        User.objects.filter(number=number).update(searchQuery=searchQuery)
        return
    addUser(number=number, searchQuery=searchQuery)
