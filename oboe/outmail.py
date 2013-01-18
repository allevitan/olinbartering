from django.core import mail
from models import Bulletin, Missive

def createBulletin(subject, message, creator, location, relevance, tag, helpbulletin, free):
    bulletin = Bulletin.objects.create(creator=creator, subject=subject, relevance=relevance, location=location, tag=tag, helpbulletin=helpbulletin, free=free)
    bulletin.save()
    missive = Missive.objects.create(message=message, bulletin=bulletin)
    missive.save()
    sendToFilter(missive)

def updateBulletin(bulletin, message):
    missive = Missive.objects.create(message=message, bulletin=bulletin)
    missive.save()
    sendToFilter(missive)

def createEmail(missive):
    updatenum = missive.bulletin.missive_set.count() - 1
    if updatenum >= 2:
        preface = "UPDATE %d: " %updatenum
    elif updatenum == 1:
        preface = "UPDATE: "
    else: preface = ""
    subject = "%s%s: %s" %(preface, missive.bulletin.tag.name, missive.bulletin.subject)
    message = "From %s:\n" % missive.bulletin.creator.user.get_full_name() 
    for mess in missive.bulletin.missive_set.order_by("-timestamp"):
        message = "%s\n\n%s" % (message, missive.message)
    return mail.EmailMessage(subject, message, headers={})

def sendToFilter(missive):
    print 'called'
    email = createEmail(missive)
    print 'created email'
    userlist = missive.bulletin.tag.userdata_set.exclude(user=missive.bulletin.creator)
    connection = mail.get_connection()
    connection.open()
    for user in userlist:
        email.to = [user.user.email]
        connection.send_messages([email])
    connection.close()


def sendToList(missive):
    email = createEmail(missive)
    if missive.bulletin.helpbulletin:
        email.to = 'helpme@lists.olin.edu'
    else: email.to = 'carpediem@lists.olin.edu'
    email.send()
