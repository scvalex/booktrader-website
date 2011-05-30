<%inherit file="/base.mak"/>

<h1>Inbox!</h1>

<h3>
  % if unread:
    ${len(unread)} unread
    % if len(unread) == 1:
      message
    % else:
      messages
    % endif
  % else:
    No unread messages
  % endif
</h3>

<ol>
  <li><a href="${request.resource_url(request.root['messages'], 'new')}">Compose</a></li>
  <li><a href="${request.resource_url(request.root['messages'])}">Inbox</a></li>
</ol>

<ol>
  % for message in messages:
    <li>
      <ul>
        % if message in unread:
          <li>Unread!</li>
        % endif
        <li>From: ${message.sender.username}</li>
        <li>To: ${message.recipient.username}</li>
        <li>${message.body}</li>
      </ul>
    </li>
  % endfor
</ol>

<%def name="title()">${parent.title()} - Inbox</%def>
