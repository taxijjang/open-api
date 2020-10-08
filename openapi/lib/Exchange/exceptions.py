import json


class MemberError(Exception):
    pass


class NotFoundMemberIdError(MemberError):
    def __init__(self, member_id):
        super(NotFoundMemberIdError, self).__init__(json.dumps({'member_id': member_id}))
        self.member_id = member_id