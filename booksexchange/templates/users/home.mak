<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />
<%namespace name="common" file="/common.mak" />

<%
current_user = request.context == request.user
username     = request.context.username
%>

<h2>
  ${request.context.username}
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
          ${', '.join([common.group_link(g, g.name)
                       for g in request.context.groups.values()])}
        </li>
    % endif
  </ul>

  % if request.context.about:
      ${request.markdown(request.context.about)}
  % endif

  % if request.user and  request.user == request.context:
      <p>
        <a href="${request.resource_url(request.root['users'], 'cp')}">
          Edit your profile
        </a>
      </p>
  % endif
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
