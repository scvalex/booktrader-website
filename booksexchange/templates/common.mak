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

<%def name="user_link(user)" buffered="True">
  <a href="${request.resource_url(user)}">${user.username}</a>
</%def>

<%def name="user_link_inner(user, inner)" buffered="True">
  <a href="${request.resource_url(user)}">${inner}</a>
</%def>

<%def name="book_link(book, inner, user = None)">
  % if user is None:
    <a href="${request.resource_url(request.root['books'], book.identifier)}">
  % else:
    <a href="${request.resource_url(user, book.identifier)}">
  % endif
    ${inner}
  </a>
</%def>

<%def name="book_cover(book)" buffered="True">
  % if book.image_links and book.image_links['thumbnail']:
      <img src="${book.image_links['thumbnail']}"
           alt="${book.title}"
           class="book_cover" />
  % else:
      <img src="${request.static_url('booksexchange:static/img/book_thumb.png')}"
           alt="${book.title}"
           class="book_cover default_cover" />
  % endif
</%def>

<%def name="group_link(group, inner)" buffered="True">
  <a href="${request.resource_url(request.root['groups'], group.identifier)}">
    ${inner}
  </a>
</%def>

<%def name="message_link(message)">
  <a href="${request.resource_url(request.root['messages'], message.identifier)}">
    ${message.subject}
  </a>
</%def>

<%def name="truncate(text, length)">
  % if len(text) > length:
      ${text[0:length]}&hellip;
  % else:
      ${text}
  % endif
</%def>

<%def name="format_date_simple(date)">
  <% from datetime import timedelta %>
  ${(date + timedelta(hours=1)).strftime("%A %d %B %Y %I:%M%p")}
</%def>

<%def name="pretty_date_simple(date)">
  <span>
    <% from datetime import datetime %>
    <% td = (datetime.utcnow() - date).seconds %>
    % if td < 60:
      ${td} seconds ago
    % elif td < 60*60:
      ${td / 60} minutes ago
    % elif td < 60*60*24:
      ${td / 60 / 60} hours ago
    % else:
      ${format_date_simple(date)}
    % endif
  </span
</%def>

<%def name="gravatar(user, size=32, class_='')">
  <a href="${request.resource_url(user)}" class="${class_ + ' gravatar'}">
    <img src="${user.gravatar(size)}" alt="${user.username}"/>
    <span>${user.username}</span>
  </a>
</%def>

<%def name="render_events(events, *args)">
  % if args:
      <ul class="${args[0] + ' events'}">
  % else:
      <ul class="events">
  % endif
    % for event in events:
        <li class="event">${render_event(event)}</li>
    % endfor
  </ul>
</%def>

<%def name="render_event(event)">
  <% from booksexchange.models import HaveEvent, WantEvent, ExchangeEvent %>
  % if isinstance(event, HaveEvent):
    ${gravatar(event.owner, 100)}
    ${book_link(event.book, book_cover(event.book))}
    <span class="user">${user_link(event.owner)}</span>
    <span class="action">
      has ${book_link(event.book, event.book.title, event.owner)}
    </span>
  % elif isinstance(event, WantEvent):
    ${gravatar(event.coveter, 100)}
    ${book_link(event.book, book_cover(event.book))}
    <span class="user">${user_link(event.coveter)}</span>
    <span class="action">
      wants ${book_link(event.book, event.book.title, event.coveter)}
    </span>
  % elif isinstance(event, ExchangeEvent):
    <div>${format_date_simple(event.date)}</div>
    <div class="event_page_cover">${book_list(event.apples, event.giver)}</div>
    <div>
      ${user_link(event.giver)}
      gave
      ${user_link(event.taker)}
    </div>
    <div class="event_page_cover">${book_list(event.oranges, event.taker)}</div>
  % endif
</%def>

<%def name="render_user(user)">
  <div class="book_short">
    ${gravatar(user, size=100, class_='cover book_cover')}
    <h3><a href="${request.resource_url(user)}">${user.username}</a></h3>
    % if user.about:
        ${request.markdown(user.about)}
    % endif
  </div>
</%def>

<%def name="users_list(users)">
  <table class="books_list">
    % while len(users) > 2:
        <tr>
          <td>
            <% user = users.pop() %>
            ${render_user(user)}
          </td>
          <td>
            <% user = users.pop() %>
            ${render_user(user)}
          </td>
        </tr>
    % endwhile
    % if len(users) > 0:
        <tr>
          <td>
            <% user = users.pop() %>
            ${render_user(user)}
          </td>
          <td class="blank"></td>
        </tr>
    % endif
  </table>
</%def>

<%def name="render_group(group)">
  <div class="book_short">
    % if group.image:
        <img src="${group.image}" alt="${group.name}" class="cover book_cover" />
    % endif
    <h3><a href="${request.resource_url(group)}">${group.name}</a></h3>
    % if group.description:
        ${request.markdown(group.description)}
    % endif
  </div>
</%def>

<%def name="groups_list(groups)">
  <table class="books_list">
    % while len(groups) > 2:
        <tr>
          <td>
            <% group = groups.pop() %>
            ${render_group(group)}
          </td>
          <td>
            <% group = groups.pop() %>
            ${render_group(group)}
          </td>
        </tr>
    % endwhile
    % if len(groups) > 0:
        <tr>
          <td>
            <% group = groups.pop() %>
            ${render_group(group)}
          </td>
          <td class="blank"></td>
        </tr>
    % endif
  </table>
</%def>

<%def name="book_list(books, owner)">
  <ul class="book_list">
    % for book in books:
      <li><a href="${request.resource_url(owner, book.identifier)}">${book_cover(book)}</a></li>
    % endfor
  </ul>
</%def>
