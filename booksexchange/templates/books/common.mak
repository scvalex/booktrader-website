<%namespace name="common" file="/common.mak" />

<%def name="render_book(book)">
    <ul>
      <li><a href="${request.resource_url(request.root['books'], book.identifier)}">${book.title}</a></li>
      ${maybe_li(book.subtitle)}

      <a href="${request.resource_url(request.root['books'], book.identifier)}">
      % if book.image_links and book.image_links['thumbnail']:
          <img src="${book.image_links['thumbnail']}" alt="${book.title}" />
      % else:
          <img src="${request.static_url('booksexchange:static/img/book_thumb.png')}" alt="${book.title}" />
      % endif
      </a>
      
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
      % if len(book.owners) > 0:
        <li>
          Owners:
          % for username in book.owners:
            ${common.user_link(book.owners[username])},
          % endfor
        </li>
      % endif
      % if len(book.coveters) > 0:
        <li>
          Coveters:
          % for username in book.coveters:
            ${common.user_link(book.coveters[username])},
          % endfor
        </li>
      % endif

    </ul>
</%def>

<%def name="maybe_li(x)">
  % if x:
    <li>${x}</li>
  % endif
</%def>

