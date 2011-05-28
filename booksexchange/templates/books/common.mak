<%def name="render_book(book)">
    <ul>
      <li>${book.title}</li>
      ${maybe_li(book.subtitle)}

      % if book.image_links and book.image_links['thumbnail']:
          <img src="${book.image_links['thumbnail']}" alt="${book.title}" />
      % else:
          <img src="${request.static_url('booksexchange:static/img/book_thumb.png')}" alt="${book.title}" />
      % endif
      
      <li>
      % for author in book.authors:
        ${author},
      % endfor
      </li>
      ${maybe_li(book.publisher)}
      ${maybe_li(book.year)}
      <li><ul>
        % for ident in book.identifiers:
          <li>${ident[0]}: ${ident[1]}</li>
        % endfor
      </ul></li>
      ${maybe_li(book.description)}
      <li>
        ${book.identifier}
      </li>
    </ul>
</%def>

<%def name="maybe_li(x)">
  % if x:
    <li>${x}</li>
  % endif
</%def>

