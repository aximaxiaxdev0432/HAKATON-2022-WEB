class CheckedException(Exception):

    def __init__(self, exc, text=None):
        if text:
            self.args = *exc.args, text,
        else:
            self.args = exc.args