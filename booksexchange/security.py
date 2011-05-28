def groupfinder(userid, request):
    if request.user is not None:
        return ['group:users']
    
    return None
