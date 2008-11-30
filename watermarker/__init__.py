VERSION = (0, 1, 1, 'pre1')

def version():
    return '%s.%s.%s-%s' % VERSION

def get_version():
    return 'django-watermark %s' % version()
