

def collect_follower_messages(user):
    messages = []
    followers = user.following
    for follower in followers:
        for msg in follower.messages:
            messages.append(msg)
    return messages