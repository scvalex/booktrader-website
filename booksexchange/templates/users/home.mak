<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />
<%namespace name="common" file="/common.mak" />

<%
current_user = request.context == request.user
username     = request.context.username
%>

<div id="user_info">
  <h2><img src="${request.context.gravatar(64)}" alt="" />${request.context.username}</h2>
</div>

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

% if current_user:
  <h3>Groups you're in:</h3>
% else:
  <h3>Groups ${username} is in</h3>
% endif
${', '.join([common.group_link(g, g.name) for g in request.context.groups.values()])}

<%def name="title()">${parent.title()} - Home</%def>
