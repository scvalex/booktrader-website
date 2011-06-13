
<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

% if google_books is not None:
  <h3>Found ${total_items} books!</h3>

  ${books_common.books_list(google_books)}

  <div id="pagination">
    % if page_index > 0:
      <a href="${books_common.paginate_url(page_index - 1, books_per_page)}">
        Previous</a>
    % endif
    % for i in page_indices:
      % if i == page_index:
        ${i}
      % else:
        <a href="${books_common.paginate_url(i, books_per_page)}">${i}</a>
      % endif
    % endfor
    % if (page_index + 1) * books_per_page < total_items:
      <a href="${books_common.paginate_url(page_index + 1, books_per_page)}">
        Next</a>
    % endif
  </div>
% endif

<%def name="title()">${parent.title()} - Search</%def>
