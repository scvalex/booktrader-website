<%inherit file="/base.mak"/>

<h2>Admin group &ldquo;${request.context.name}&rdquo;</h2>


${form}

<%def name="title()">${parent.title()} - Groups - ${request.context.name} - Admin</%def>
