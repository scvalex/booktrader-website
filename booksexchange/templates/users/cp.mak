<%inherit file="/base.mak"/>

<h2>Edit your profile</h2>
${form}

<p>
  <a href="${request.resource_url(request.user)}">View your profile</a>
</p>

<%def name="title()">${parent.title()} - User CP</%def>
