<%inherit file="/base.mak"/>

<h3>Admin group ${context}</h3>


${form}

% if request.context.domains:
    <h3>Authorized domains</h3>
    <ul>
      % for d in request.context.domains:
         <li>${d}</li>
      % endfor
    </ul>
% endif
