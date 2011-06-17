## Copyright 2011 the authors of BookTrader (see the AUTHORS file included).
##
## This file is part of BookTrader.
##
## BookTrader is free software: you can redistribute it and/or modify it
## under the terms of the GNU Affero General Public License as published
## by the Free Software Foundation, version 3 of the License.
##
## BookTrader is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even any implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## Affero General Public License version 3 for more details.
##
## You should have received a copy of the GNU Affero General Public
## License version 3 along with BookTrader. If not, see:
## http://www.gnu.org/licenses/

<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />
<%namespace name="books_common" file="/books/common.mak" />

<% from booksexchange.models import Offer %>

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
    % if isinstance(msg_root[0], Offer):
      % if not msg_root[0].accepted:
        <li><a href="${request.resource_url(msg_root[0], 'edit_offer')}">Edit Offer</a></li>
      % endif
      % if request.user not in msg_root[0].accepted:
        <li><a href="${request.resource_url(msg_root[0], 'accept_offer')}">Accept Offer</a></li>
      % endif
      % if len(msg_root[0].accepted) == 2 and request.user not in msg_root[0].left_feedback:
        <li><a href="${request.resource_url(msg_root[0], 'complete')}">Leave feedback</a></li>
      % endif
    % endif
    <li><a href="${request.resource_url(msg_root[-1], 'offer')}">Make New Offer</a></li>
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
    % if isinstance(message, Offer):
      <div class="offer_info">
        <div>
          <a href="${request.resource_url(message.sender)}">
            ${common.gravatar(message.sender, 64)}
          </a>
          ${render_book_list(message.apples, message.sender)}
        </div>
        <div class="vs_text">for</div>
        <div>
          <a href="${request.resource_url(message.recipient)}">
            ${common.gravatar(message.recipient, 64)}
          </a>
          ${render_book_list(message.oranges, message.recipient)}
        </div>
      </div>
    % endif
    <div class="actual_message">
      <div class="from">${common.user_link(message.sender)}</div>
      <div class="date">${common.format_date_simple(message.date)}</div>
      <div class="to">${common.user_link(message.recipient)}</div>
      <div class="subject">${common.message_link(message)}</div>
      <div class="body">${message.body}</div>
    </div>
    <div class="clear"></div>
  </${top}>
</%def>

<%def name="render_book_list(books, owner)">
  <ul class="book_list">
    % for book in books:
      <li><a href="${request.resource_url(owner, book.identifier)}">${common.book_cover(book)}</a></li>
    % endfor
  </ul>
</%def>
