<%inherit file="/base.mak"/>

<h3>Join group ${request.context.name}</h3>

% if form:
    The group requires an email of the following domains:
    ${', '.join(['@' + d for d in request.context.domains])}

    ${form}
% else:
    <p>
      A verification token has been generated, please check your email
      to join the group.
    </p>
% endif

