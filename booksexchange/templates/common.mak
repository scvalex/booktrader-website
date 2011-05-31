<%def name="user_link(user)">
  <a href="${request.resource_url(user)}">${user.username}</a>
</%def>

<%def name="user_link_inner(user, inner)">
  <a href="${request.resource_url(user)}">${inner}</a>
</%def>

<%def name="format_book_title(book)">
  ${book.title}
  % if book.subtitle:
    - ${book.subtitle}
  % endif
  % if book.authors:
    by
    % for author in book.authors:
      ${author}, 
    % endfor
  % endif
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

