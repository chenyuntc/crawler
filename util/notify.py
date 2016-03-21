__author__ = 'cy'
from hypchat import HypChat

__users__ = ['cyfall@163.com', 'b@b.com']
__token__='autC8mgWDMxXdndDirfi7YpSeNygh96b96FXwIZY'
def wrap(message):
    return message


def send_notify(data):

    hp = HypChat(__token__)
    for user in __users__:
        try:
            t_user = hp.get_user(user)
            message=wrap(data)
            t_user.message(message)
        except Exception as e:
            print e
    return True



send_notify('hello there')





