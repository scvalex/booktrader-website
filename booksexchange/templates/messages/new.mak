<%inherit file="/base.mak"/>

<h2>New ${typ}</h2>

${form}

<div class="conversation_controls">
    <a href="${request.referer}">Cancel</a>
</div>

<%def name="title()">${parent.title()} - New Message</%def>
