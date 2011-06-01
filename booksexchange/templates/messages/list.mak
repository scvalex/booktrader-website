<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />
<%namespace name="books_common" file="/books/common.mak" />

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
<ul class="conversation_controls">
  <li>
    <a href="${request.resource_url(request.root['messages'], 'new')}">Compose</a>
  </li>
  <li>
    <a href="${request.resource_url(request.root['messages'], 'list')}">Inbox</a>
  </li>
</ul>

% if msg_root:
  <ol class="conversation">
    % for m in conversations[msg_root.identifier]:
      ${show_message(m)}
    % endfor
    <li class="clear"></li>
  </ol>
  <ul class="conversation_controls clear">
    <li><a href="${request.resource_url(msg_root, 'reply')}">Reply</a></li>
    <li><a href="${request.resource_url(msg_root, 'offer')}">Make Offer</a></li>
    <% from booksexchange.models import Offer %>
    % if request.user is not m.sender and isinstance(m, Offer):
      <li><a href="${request.resource_url(m, 'complete')}">Trade completed</a></li>
    % endif
    <li><a href="${request.referer}">Back</a></li>
  </ul>
% else:
  <table class="inbox">
    <thead>
      <tr>
        <td>From/To</td>
        <td>Subject</td>
        <td>Date</td>
      </tr>
    </thead>
    <tbody>
      % for message in conversation_list:
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
          <td>${common.format_date_simple(message.date)}</td>
        </tr>
      % endfor
    </tbody>
  </table>
% endif

<%def name="title()">${parent.title()} - Inbox</%def>

<%def name="show_message(message, top='li')">
  <${top} class="message clear">
    <div class="actual_message">
      <div class="from">${common.user_link(message.sender)}</div>
      <div class="date">${common.format_date_simple(message.date)}</div>
      <div class="to">${common.user_link(message.recipient)}</div>
      <div class="subject">${common.message_link(message)}</div>
      <div class="body">${message.body}</div>
    </div>
    <div class="offer_info">
      <% from booksexchange.models import Offer %>
      % if isinstance(message, Offer):
        % if message.sender is request.user:
          <div>${books_common.render_book_short(message.apples, request.user)}</div>
        % else:
          <div>${books_common.render_book_short(message.oranges, request.user)}</div>
        % endif
        <div class="vs_text">for</div>
        % if message.sender is request.user:
          <div>${books_common.render_book_short(message.oranges, message.sender)}</div>
        % else:
          <div>${books_common.render_book_short(message.apples, message.sender)}</div>
        % endif
      % endif
    </div>
    <div class="clear"></div>
  </${top}>
</%def>
