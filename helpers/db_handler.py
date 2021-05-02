class DBHandler:

    __instance = None

    # TODO
    def __init__(self):
        DBHandler.__instance = self

    @staticmethod
    def get_instance():
        if DBHandler.__instance is None:
            DBHandler()
        return DBHandler.__instance

    #TODO
    def subscribe(self, body):
        email = body['email']
        phone_number = body['phone_number']
        for subscription in body['subscriptions']:
            vaccine = subscription['vaccine']
            age_group = subscription['age_group']
            district_id = subscription['district_id']
        return False