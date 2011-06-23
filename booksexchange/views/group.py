# Copyright 2011 the authors of BookTrader (see the AUTHORS file included).
#
# This file is part of BookTrader.
#
# BookTrader is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3 of the License.
#
# BookTrader is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even any implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License version 3 for more details.
#
# You should have received a copy of the GNU Affero General Public
# License version 3 along with BookTrader. If not, see:
# http://www.gnu.org/licenses/

from booksexchange.views.common import *


@view_config(context=Groups, name='create', permission='loggedin',
             renderer='groups/create_group.mak')
def create_group(context, request):
    schema = GroupSchema()
    form   = deform.Form(schema, buttons=('Create Group',))

    if 'Create Group' in request.params:
        controls = request.params.items()

        try:
            group_data = form.validate(controls)
        except deform.ValidationFailure, e:
            return {'form': render_form(e)}

        new_group = Group(group_data['name'],
                          group_data['description'],
                          group_data['type'])
        context[new_group.identifier] = new_group

        new_group.add_member(request.user)
        new_group.add_owner(request.user)
        request.user.add_group(new_group)
        request.root['users'].update(request.user)
        request.root['groups'].update(new_group)

        request.session.flash('Your group has been created.')

        raise HTTPFound(location = request.resource_url(new_group))

    return {'form': render_form(form)}

@view_config(context=Group, renderer='groups/view.mak', permission='view_group')
def view_group(context, request):
    return {}


def join_group_success(context, request):
    request.user.add_group(context)
    context.add_member(request.user)
    request.root['users'].update(request.user)
    request.root['groups'].update(context)

    request.session.flash('You are now a member of ' + context.name + '!')

    raise HTTPFound(location = request.resource_url(context))


@view_config(context=Group, name='confirm_join', permission='join_group')
def confirm_join_group(context, request):
    if 'token' in request.params:
        if context.confirm_user(request.user, request.params['token']):
            join_group_success(context, request)
        else:
            request.session.flash('The token provided is wrong, please try again.')
            raise HTTPFound(location = request.resource_url(context, 'join'))

    raise HTTPBadRequest('No token provided.')

@view_config(context=Group, name='join', permission='join_group',
             renderer='groups/join.mak')
def join_group(context, request):
    if context.type == 'public':
        join_group_success(context, request)

    elif context.type == 'private':

        def validate_email(node, value):
            colander.Length(max=255)(node, value)

            for domain in context.domains:
                if value.endswith('@' + domain):
                    return

            error_email = "The email you inserted doesn't belong " + \
                          "to one of the required domains."
            raise colander.Invalid(node, error_email)

        class GroupEmail(colander.MappingSchema):
            email = colander.SchemaNode(colander.String(), validator=validate_email)

        form = deform.Form(schema=GroupEmail(), buttons=('Join',))

        if 'Join' in request.params:
            controls = request.params.items()

            try:
                data = form.validate(controls)
            except deform.ValidationFailure, e:
                return {'form': render_form(e)}

            token = context.generate_token(request.user)

            confirm_url = request.resource_url(context, 'confirm_join',
                                               query = {'token': token})

            email_body = "Dear " + request.user.username + ",\n\n" + \
                         "To join group " + context.name +"," \
                         "please click visit this link: " + confirm_url + ".\n\n" + \
                         "The BookTrader team."


            send_email(email_body, 'BookTrader group.',
                       [data['email']], request.registry.settings)

            return {'form':None}

        return {'form': render_form(form)}


@view_config(context=Group, name='admin', permission='admin_group',
             renderer='groups/admin.mak')
def admin_group(context, request):

    class DomainsSchema(colander.SequenceSchema):
        domain = colander.SchemaNode(utf8_string(),
                                     validator = colander.Length(min=3, max=255),
                                     title     = 'Domain')
    class GroupAdminSchema(GroupSchema):
        domains = DomainsSchema()


    if context.type == 'public':
        schema = GroupSchema()
    else:
        schema = GroupAdminSchema()
        schema['domains'].default = context.domains


    form = deform.Form(schema, buttons=('Submit',))

    choices = [(context.type, context.type.capitalize())]
    for t in Group.types:
        if t != context.type:
            choices.append((t, t.capitalize()))

    form.schema['type'].widget.values  = choices
    form.schema['name'].default        = context.name
    form.schema['description'].default = context.description
    if context.image:
        form.schema['image'].default   = context.image

    if 'Submit' in request.params:
        controls = request.params.items()

        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            return {'form': render_form(e)}

        context.name        = data['name']
        context.description = data['description']
        context.type        = data['type']
        context.image       = data['image']

        if 'domains' in data:
            context.domains = data['domains']

        request.root['groups'].update(context)

        raise HTTPFound(location = request.url)


    return {'form': render_form(form)}
