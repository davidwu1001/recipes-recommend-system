def _escape(s):
    """
    将s中的单引号'转义为\\'
    :param s:
    :return:
    """
    s = s.replace("'","\\'")
    return s

def _unescape(s):
    s = s.replace("\\'",".")
    return s
