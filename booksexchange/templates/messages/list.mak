<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />

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
  <li><a href="${request.resource_url(request.root['messages'], 'list')}">Inbox</a></li>
</ol>

% if msg:
  Reading message!
% else:
  <ol>
    % for message in messages:
      <li>
        <ul>
          % if message in unread:
            <li>Unread!</li>
          % endif
          <li>From: ${common.user_link(message.sender)}</li>
          <li>To: ${common.user_link(message.recipient)}</li>
          <li>Subject: ${common.message_link(message)}</li>
          <li>${message.body}</li>
        </ul>
      </li>
    % endfor
  </ol>
% endif

<%def name="title()">${parent.title()} - Inbox</%def>
