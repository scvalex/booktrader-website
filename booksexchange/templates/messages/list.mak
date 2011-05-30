<%inherit file="/base.mak"/>

<h3>Inbox!</h3>

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

<%def name="title()">${parent.title()} - New Message</%def>
