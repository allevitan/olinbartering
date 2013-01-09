import time

def pull_suffix(filename):
    splitfile = filename.split('.')
    return splitfile[-1]
    
def create_profpic_path(instance, filename):
    return 'profiledata/%s/pic.%s' % (instance.user.username, pull_suffix(filename))

def create_missivepic_path(instance, filename):
    return 'bulletindata/%s/missive%02d/pic.%s' % (instance.bulletin.creation.strftime('%C%m%d_%H%M%S'), instance.number, pull_suffix(filename))


#Test Code
if __name__ == '__main__':
    
    #note: pull_suffix works
    print pull_suffix('hi.asd')
    
