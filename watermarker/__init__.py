VERSION = (0, 1, 5, 'pre1')

def version():
    return '%s.%s.%s-%s' % VERSION

def get_version():
    return 'django-watermark %s' % version()
