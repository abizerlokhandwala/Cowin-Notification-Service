class EmailHandler:

    __instance = None

    # TODO
    def __init__(self):
        EmailHandler.__instance = self

    @staticmethod
    def get_instance():
        if EmailHandler.__instance is None:
            EmailHandler()
        return EmailHandler.__instance

    # TODO
    def sendVerificationEmail(self, email):
        return