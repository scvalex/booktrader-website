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
    % for m in msg_root:
      ${show_message(m)}
    % endfor
    <li class="clear"></li>
  </ol>
  <ul class="conversation_controls clear">
    <li><a href="${request.resource_url(msg_root[-1], 'reply')}">Reply</a></li>
    <li><a href="${request.resource_url(msg_root[-1], 'offer')}">Make Offer</a></li>
    <li><a href="${request.referer}">Back</a></li>
  </ul>
% else:
  <table class="inbox">
    <tbody>
      % for username in conversation_list:
        % if username in unread:
          <tr class="unread">
        % else:
          <tr>
        % endif
          <td>${common.user_link(request.root['users'][username])}</td>
          <td class="summary_message_body">
            ${common.message_link(conversations[username][-1])}
            -
            ${conversations[username][-1].body[:32]}...
          </td>
          <td>
            ${common.format_date_simple(conversations[username][-1].date)}
          </td>
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
