def groupfinder(userid, request):
    if request.user is not None:
        groups = ['group:users']

        for group in request.user.groups.values():
            groups.append(group.members_group)

            if request.user.username in group.owners:
                groups.append(group.owners_group)
        
        return groups

    return None
