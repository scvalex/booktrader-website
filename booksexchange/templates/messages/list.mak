<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />

<h2>Inbox</h2>

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
  <ul>
    <li>From: ${common.user_link(msg.sender)}</li>
    <li>To: ${common.user_link(msg.recipient)}</li>
    <li>Subject: ${common.message_link(msg)}</li>
    <li>${msg.body}</li>
    <li><h3><a href="${request.resource_url(msg, 'reply')}">Reply!</a></h3></li>
  </ul>
% else:
  <table class="messageList">
    <thead>
      <tr>
        <td>From/To</td>
        <td>Subject</td>
        <td>Date</td>
      </tr>
    </thead>
    <tbody>
      % for message in messages:
        % if message in unread:
          <tr class="unread">
        % else:
          <tr>
        % endif
          <td>
            % if message.sender == request.user:
              ${common.user_link(message.recipient)}
            % else:
              ${common.user_link(message.sender)}
            % endif
          </td>
          <td>${common.message_link(message)}</td>
          <td>${message.date}</td>
        </tr>
      % endfor
    </tbody>
  </table>
% endif

<%def name="title()">${parent.title()} - Inbox</%def>
