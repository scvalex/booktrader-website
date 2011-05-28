<%inherit file="/base.mak"/>

<h3>Your books!</h3>

Add more books <a href="/books/search">here</a>.

<ol>
  % for book in books:
    <li><ul>
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
    </ul></li>
  % endfor
</ol>

<%def name="title()">${parent.title()} - List</%def>

<%def name="maybe_li(x)">
  % if x:
    <li>${x}</li>
  % endif
</%def>
