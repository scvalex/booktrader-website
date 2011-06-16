## Copyright 2011 the authors of BookTrader (see the AUTHORS file included).
##
## This file is part of BookTrader.
##
## BookTrader is free software: you can redistribute it and/or modify it
## under the terms of the GNU Affero General Public License as published
## by the Free Software Foundation, version 3 of the License.
##
## BookTrader is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even any implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## Affero General Public License version 3 for more details.
##
## You should have received a copy of the GNU Affero General Public
## License version 3 along with BookTrader. If not, see:
## http://www.gnu.org/licenses/

<%inherit file="/base.mak" />

<%namespace name="common" file="/common.mak" />

% if error:
    <h2>Error: ${error}</h2>
% else:

<%
if search_type == 'users':
    render_func = common.users_list
elif search_type == 'groups':
    render_func = common.groups_list
%>

<h2>
  Found ${len(items)} ${search_type}
</h2>

${render_func(items)}

% endif
