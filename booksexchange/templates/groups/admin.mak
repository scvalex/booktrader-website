<%inherit file="/base.mak"/>

<h2>Admin group &ldquo;${request.context.name}&rdquo;</h2>


${form}

% if request.context.domains:
    <h3>Authorized domains</h3>
    <ul>
      % for d in request.context.domains:
         <li>${d}</li>
      % endfor
    </ul>
% endif

<%def name="title()">${parent.title()} - Groups - ${request.context.name} - Admin</%def>
