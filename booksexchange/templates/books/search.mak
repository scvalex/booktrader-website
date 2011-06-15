## Copyright 2011 the authors of BookTrader (see the AUTHORS file included).
##
## This file is part of BookTrader.
##
## BookTrader is free software: you can redistribute it and/or modify it
## under the terms of the GNU Affero General Public License as published
## by the Free Software Foundation, version 3 of the License.
##
## BookTrader is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even any implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## Affero General Public License version 3 for more details.
##
## You should have received a copy of the GNU Affero General Public
## License version 3 along with BookTrader. If not, see:
## http://www.gnu.org/licenses/


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
