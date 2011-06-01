<%def name="user_link(user)">
  <a href="${request.resource_url(user)}">${user.username}</a>
</%def>

<%def name="user_link_inner(user, inner)">
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

<%def name="book_cover(book)">
  % if book.image_links and book.image_links['thumbnail']:
      <img src="${book.image_links['thumbnail']}"
           alt="${book.title}" />
  % else:
      <img src="${request.static_url('booksexchange:static/img/book_thumb.png')}"
           alt="${book.title}" />
  % endif
</%def>

<%def name="group_link(group, inner)">
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
  ${date.strftime("%A %d %B %Y %I:%M%p")}
</%def>

<%def name="gravatar(user)">
  <a href="${request.resource_url(user)}">
    <img src="${user.gravatar(32)}" alt="${user.username}"/>
    <span>${user.username}</span>
  </a>
</%def>

<%def name="render_event(event)">
  <% from booksexchange.models import HaveEvent, WantEvent, ExchangeEvent %>
  % if isinstance(event, HaveEvent):
    <div>${format_date_simple(event.date)}</div>
    <div class="event_page_cover">${book_cover(event.book)}</div>
    <div>
      ${user_link(event.owner)}
      has
      ${book_link(event.book, event.book.format_title(), event.owner)}
    </div>
  % elif isinstance(event, WantEvent):
    <div>${format_date_simple(event.date)}</div>
    <div class="event_page_cover">${book_cover(event.book)}</div>
    <div>
      ${user_link(event.coveter)}
      wants
      ${book_link(event.book, event.book.format_title())}
    </div>
  % elif isinstance(event, ExchangeEvent):
    <div>${format_date_simple(event.date)}</div>
    <div class="event_page_cover">${book_cover(event.apples)}</div>
    <div>
      ${user_link(event.giver)}
      gave
      ${user_link(event.taker)}
      ${book_link(event.apples, event.apples.format_title(), event.taker)}
      for
      ${book_link(event.oranges, event.oranges.format_title(), event.giver)}
    </div>
    <div class="event_page_cover">${book_cover(event.oranges)}</div>
  % endif
</%def>
