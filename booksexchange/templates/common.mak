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

<%def name="gravatar(user, size=32)">
  <a href="${request.resource_url(user)}" class="gravatar">
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
    <div class="event_page_cover">${book_cover(event.apples)}</div>
    <div>
      ${user_link(event.giver)}
      gave
      ${user_link(event.taker)}
      ${book_link(event.apples, event.apples.title, event.taker)}
      for
      ${book_link(event.oranges, event.oranges.title, event.giver)}
    </div>
    <div class="event_page_cover">${book_cover(event.oranges)}</div>
  % endif
</%def>
