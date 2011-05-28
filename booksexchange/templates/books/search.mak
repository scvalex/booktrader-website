<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

<ul id="books_list">
  <% left = True %>
  % for book in result:
    % if left:
        <li>
    % else:
        <li class="right">
    % endif
      ${books_common.render_book_short(book)}
    </li>
    <% left = not left %>
  % endfor
</ul>

<%def name="title()">${parent.title()} - Search</%def>
