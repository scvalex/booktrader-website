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

<%namespace name="books_common" file="/books/common.mak" />
<%namespace name="common" file="/common.mak" />

<%
current_user = request.context == request.user
username     = request.context.username
%>

<h2>
  ${request.context.username}
  <span class="feedbacks_score">
    <%
    score = request.context.feedbacks_score
    if score > 95:
        color = "green"
    elif score > 80:
        color = "yellow"
    else:
        color = "red"
    %>
    
    <span class=${color}>
      ${request.context.feedbacks_score}%
    </span> (${len(request.context.feedbacks)})
  </span>
</h2>

<img src="${request.context.gravatar(64)}"
     alt="${request.context.username}"
     class="gravatar" />

<div id="profile">
  <ul id="user_info">
    % if request.context.location:
         <li><strong>Location:</strong> ${request.context.location}</li>
    % endif
    % if request.context.groups:
        <li><strong>Groups:</strong>
          ${common.commify(request.context.groups.values(),
                           lambda g: common.group_link(g, g.name))}
        </li>
    % endif
  </ul>

  % if request.user and  request.user == request.context:
      <p>
        <a href="${request.resource_url(request.root['users'], 'cp')}">
          Edit your profile
        </a>
      </p>
  % endif
</div>

<hr style="visibility: hidden; clear:both" />
% if request.context.about:
    ${request.markdown(request.context.about)}
% endif


<div id="real_stuff">
  % if current_user:
    <h3>Your books</h3>
  % else:
    <h3>${username}'s books</h3>
  % endif

  ${books_common.books_list(owned, request.context)}

  % if current_user:
    <h3>Books you want</h3>
  % else:
    <h3>Books ${username} wants</h3>
  % endif

  ${books_common.books_list(want)}
</div>
<div id="stuff_in_flux">
  <h3>History</h3>
  ${common.render_events(events[:15])}
</div>


<%def name="title()">${parent.title()} - Home</%def>
