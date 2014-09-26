VERSION = (0, 1, 6, 'special')

def version():
    return '%s.%s.%s-%s' % VERSION

def get_version():
    return 'django-watermark %s' % version()
