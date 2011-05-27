<%inherit file="/base.mak"/>

${form}

<ol>
  % for book in result:
    <li><ul>
      <li>${book.title}</li>
      % if book.subtitle:
        <li>${book.subtitle}</li>
      % endif
      <li>
      % for author in book.authors:
        ${author}, 
      % endfor
      </li>
      % if book.publisher:
        <li>${book.publisher}</li>
      % endif
      <li><ul>
        % for ident in book.identifiers:
          <li>${ident[0]}: ${ident[1]}</li>
        % endfor
      </ul></li>
      % if book.description:
        <li>${book.description}</li>
      % endif
    </ul></li>
  % endfor
</ol>

<%def name="title()">${parent.title()} - Search</%def>
