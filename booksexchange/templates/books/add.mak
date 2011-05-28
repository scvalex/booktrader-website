<%inherit file="/base.mak"/>

% if status == 'ok':
  <h3>Book added!</h3>
  <ul>
    <li>${book.title}</li>
    ${maybe_li(book.subtitle)}
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
% endif

See your bookshelf <a href="/books/list">here</a>.

<%def name="title()">${parent.title()} - Search</%def>

<%def name="maybe_li(x)">
  % if x:
    <li>${x}</li>
  % endif
</%def>
