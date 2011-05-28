<%def name="user_link(user)">
  <a href="${request.resource_url(user)}">${user.username}</a>
</%def>
