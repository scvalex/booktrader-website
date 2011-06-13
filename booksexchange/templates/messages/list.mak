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
  <h3>Offers</h3>
  <% from booksexchange.models import Offer %>
  <table class="inbox">
    <tbody>
      ${show_message_list(conversation_list, conversations, lambda msg: isinstance(msg, Offer))}
    </tbody>
  </table>
  <h3>Messages</h3>
  <table class="inbox">
    <tbody>
      ${show_message_list(conversation_list, conversations, lambda msg: not isinstance(msg, Offer))}
    </tbody>
  </table>
% endif

<%def name="title()">${parent.title()} - Inbox</%def>

<%def name="show_message_list(conversation_list, conversations, filter)">
  % for conversation in conversation_list:
    <% if not filter(conversations[conversation][0]): continue %>
    <% other = conversations[conversation][-1].sender %>
    <% if other is request.user:
       other = conversations[conversation][-1].recipient %>
    % if conversation in unread:
      <tr class="unread">
    % else:
      <tr>
    % endif
    <td>${common.user_link(other)}</td>
    <td class="summary_message_body">
      ${common.message_link(conversations[conversation][-1])}
      -
      ${conversations[conversation][-1].body[:32]}...
    </td>
    <td>
      ${common.pretty_date_simple(conversations[conversation][-1].date)}
    </td>
  </tr>
  % endfor
</%def>

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
          <div>${render_book_list(message.apples, request.user)}</div>
        % else:
          <div>${render_book_list(message.oranges, request.user)}</div>
        % endif
        <div class="vs_text">for</div>
        % if message.sender is request.user:
          <div>${render_book_list(message.oranges, message.sender)}</div>
        % else:
          <div>${render_book_list(message.apples, message.sender)}</div>
        % endif
      % endif
    </div>
    <div class="clear"></div>
  </${top}>
</%def>

<%def name="render_book_list(books, owner)">
  % for book in books:
    <div>${books_common.render_book_short(book, owner)}</div>
  % endfor
</%def>
