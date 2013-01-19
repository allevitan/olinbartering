from django.core import mail
from models import Bulletin, Missive, Reply_Thread, Reply

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

def replyToBulletin(bulletin, message, user, public):
    #generate new thread if needed
    if bulletin.reply_thread_set.filter(replier=user).exists():
        thread = (bulletin.reply_thread_set.filter(replier=user)[0])
    else:
        thread = Reply_Thread.objects.create(bulletin=bulletin, replier=user)
        #save info
        thread.save()
    reply = Reply.objects.create(public=public, sender=user, message=message, thread=thread)
    reply.save()
    sendToCreator(reply)


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
    return mail.EmailMessage(subject, message)

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

def sendToCreator(reply):
    subject = "RE: %s" % reply.thread.bulletin.subject
    message = "From %s:\n%s" %(reply.get_replier_name(),reply.message)
    address = reply.get_to_email()
    email = mail.EmailMessage(subject, message)
    email.to = [address]
    email.send()
