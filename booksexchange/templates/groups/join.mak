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

<%inherit file="/base.mak"/>

<h2>Join group ${request.context.name}</h2>

% if form:
    The group requires an email of the following domains:
    ${', '.join(['@' + d for d in request.context.domains])}

    ${form}
% else:
    <p>
      A verification token has been generated, please check your email
      to join the group.
    </p>
% endif

