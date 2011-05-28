<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

<ul id="books_list">
  % for book in result:
    <li>
      ${books_common.render_book_short(book)}
    </li>
  % endfor
</ul>

<%def name="title()">${parent.title()} - Search</%def>
