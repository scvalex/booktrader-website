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
    % if isinstance(msg_root[0], Offer):
      <div class="offer_info">
        <div class="left">
          % if msg_root[0].sender in msg_root[0].accepted:
            <span class="accepted">✔</span>
          % endif
          <span>${msg_root[0].sender.username}</span>
          ${common.gravatar(msg_root[0].sender, 64)}
          ${common.book_list(msg_root[0].apples, msg_root[0].sender)}
        </div>
        <div class="right">
          ${common.gravatar(msg_root[0].recipient, 64)}
          <span>${msg_root[0].recipient.username}</span>
          % if msg_root[0].recipient in msg_root[0].accepted:
            <span class="accepted">✔</span>
          % endif
          ${common.book_list(msg_root[0].oranges, msg_root[0].recipient)}
        </div>
      </div>
  <ol class="conversation offer_conversation">
    % else:
  <ol class="conversation">
    % endif

    % for m in msg_root[:-1]:
      ${show_message(m)}
    % endfor
    ${show_message(msg_root[-1], last=True)}
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
    % if request.referer is None:
      <a href="${request.resource_url(request.root['messages'], 'list')}">Back</a>
    % else:
      <a href="${request.referer}">Back</a>
    % endif
  </ul>
% else:
  <div class="inbox_offers inbox">
    <h3>Offers</h3>
    <% from booksexchange.models import Offer %>
    <ul>
      ${show_message_list(conversation_list, conversations, lambda msg: isinstance(msg, Offer))}
    </ul>
  </div>
  <div class="inbox_messages inbox">
    <h3>Messages</h3>
    <ul>
      ${show_message_list(conversation_list, conversations, lambda msg: not isinstance(msg, Offer))}
    </ul>
  </div>
% endif

<%def name="title()">${parent.title()} - Inbox</%def>

<%def name="show_message_list(conversation_list, conversations, filter)">
  % for conversation in conversation_list:
    <%
    if not filter(conversations[conversation][0]):
        continue
    message = conversations[conversation][-1]
    other = message.sender
    if other is request.user:
        other = message.recipient
    %>
    % if conversation in unread:
      <li class="unread">
    % else:
      <li>
    % endif
    ${common.gravatar(other, size=40)}
    <a href="${request.resource_url(message)}" class="message_link">
      ${common.pretty_date_simple(conversations[conversation][-1].date)}
      ${other.username}<br/>
      % if message.subject:
          ${message.subject}
      % else:
          ${message.body}
      % endif
    </a>
  </li>
  % endfor
</%def>

<%def name="show_message(message, top='li', last=False)">
  <${top} class="message clear">
    <%
    bclass = ''
    if last:
       bclass = ' last_message'
    %>
    <div class="actual_message${bclass}">
      <div class="from">${common.user_link(message.sender)}</div>
      <div class="date">${common.format_date_simple(message.date)}</div>
      <div class="to">${common.user_link(message.recipient)}</div>
      <div class="subject">${message.subject}</div>
      <div class="body${bclass}">${request.markdown(message.body)}</div>
    </div>
  </${top}>
</%def>
