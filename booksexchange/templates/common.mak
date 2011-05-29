<%def name="user_link(user)">
  <a href="${request.resource_url(user)}">${user.username}</a>
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

<%def name="book_link(book, inner)">
  <a href="${request.resource_url(request.root['books'], book.identifier)}">
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
