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
          <span>${msg_root[0].sender.username}</span>
          ${common.gravatar(msg_root[0].sender, 64)}
          ${common.book_list(msg_root[0].apples, msg_root[0].sender)}
        </div>
        <div class="right">
          ${common.gravatar(msg_root[0].recipient, 64)}
          <span>${msg_root[0].recipient.username}</span>
          ${common.book_list(msg_root[0].oranges, msg_root[0].recipient)}
        </div>
      </div>
    % endif

  <ol class="conversation">

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
      <div class="subject">${common.message_link(message)}</div>
      <div class="body${bclass}">${request.markdown(message.body)}</div>
    </div>
  </${top}>
</%def>
