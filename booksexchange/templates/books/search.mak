<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

<h3>Found ${total_items} books!</h3>

<ul id="books_list">
  % for book in result:
    <li>
      ${books_common.render_book_short(book)}
    </li>
  % endfor
</ul>

% if prev_url:
  <a href="${prev_url}">Previous</a>
% endif
% if next_url:
  <a href="${next_url}">Next</a>
% endif


<%def name="title()">${parent.title()} - Search</%def>
