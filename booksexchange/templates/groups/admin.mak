<%inherit file="/base.mak"/>

<h2>Admin group &ldquo;<a href="${request.resource_url(request.context)}">${request.context.name}</a>&rdquo;</h2>


${form}

<%def name="title()">${parent.title()} - Groups - ${request.context.name} - Admin</%def>
