<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

% if result:
  <h3>Found ${total_items} books!</h3>

  <ul class="books_list">
    % for book in result:
      <li>
        ${books_common.render_book_short(book)}
      </li>
    % endfor
  </ul>

  % if prev_url:
    <a href="${prev_url}">Previous</a>
  % endif
  % for i in page_indices:
    % if i == page_index:
      ${i}
    % else:
      <a href="${make_url(i)}">${i}</a>
    % endif
  % endfor
  % if next_url:
    <a href="${next_url}">Next</a>
  % endif
% endif

<%def name="title()">${parent.title()} - Search</%def>
