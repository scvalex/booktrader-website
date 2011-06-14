<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />

<% group = request.context %>

<h2>${group.name}</h3>
% if request.user:
    <ul id="group_actions">
      % if request.user.username not in group.members:
          <li><a href="${request.resource_url(group, 'join')}">Join group</a></li>
      % elif request.user.username in group.owners:
          <li><a href="${request.resource_url(group, 'admin')}">Admin group</a></li>
      % endif
    </ul>
% endif
<p>
  % if group.image:
      <img src="${group.image}" alt="${group.name}" id="group_image" />
  % endif
  ${request.markdown(group.description)}
</p>

<div id="group_members">
  <div class="owners">
    <h3 class="group_clear">Owners</h3>
    ${group_members(group.owners.values())}
  </div>
  <div class="owners">
    <h3>Members</h3>
    ${group_members(group.members.values())}
  </div>
</div>

<%def name="title()">${parent.title()} - Groups - ${request.context.name}</%def>

<%def name="group_members(users)">
   <ul>
      % for u in users:
          <li>
            ${common.gravatar(u, size=64)}
          </li>
      % endfor
   </ul>
</%def>
