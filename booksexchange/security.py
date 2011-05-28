def groupfinder(userid, request):
    users = request.root['users']
    
    if userid in users:
        return ['group:users']
    return None
