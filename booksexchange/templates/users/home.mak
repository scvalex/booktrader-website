<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />
<%namespace name="common" file="/common.mak" />

<%
current_user = request.context == request.user
username     = request.context.username
%>

<div>
  <h2><img src="${request.context.gravatar(64)}" alt="" />${request.context.username}</h2>
</div>

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

  % if current_user:
    <h3>Groups you're in:</h3>
  % else:
    <h3>Groups ${username} is in</h3>
  % endif
  ${', '.join([common.group_link(g, g.name) for g in request.context.groups.values()])}
</div>
<div id="stuff_in_flux">
  <h3>History</h3>
  <ul>
    % for event in events:
      <li>
        ${common.render_event(event)}
        <div class="clear"></div>
      </li>
    % endfor
  </ul>
</div>

<%def name="title()">${parent.title()} - Home</%def>
