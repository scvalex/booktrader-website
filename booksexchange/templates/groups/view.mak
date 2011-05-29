<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />

<% group = request.context %>

<h2>${group.name}</h3>
<p>${group.description}<p>
<h3>Owners</h3>
${', '.join([common.user_link(u) for u in group.owners.values()])}
<h3>Members</h3>
${', '.join([common.user_link(u) for u in group.members.values()])}

