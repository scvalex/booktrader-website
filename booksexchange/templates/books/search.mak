<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

% if result is not None:
  <h3>Found ${total_items} books!</h3>

  <table class="books_list" style="border-spacing: 10px;">
    <% result.reverse() %>
    % while len(result) > 1:
        <tr>
          <td>${books_common.render_book_short(result.pop())}</td>
          <td>${books_common.render_book_short(result.pop())}</td>
        </tr>
    % endwhile
    % if len(result) > 0:
        <tr>
          <td>${books_common.render_book_short(result.pop())}</td>
          <td></td>
        </tr>
    % endif
  </table>

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
