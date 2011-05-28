<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

% if not username:
  <h3>Your books!</h3>
% else:
  <h3>${username}'s books!</h3>
% endif

<ol>
  % for book in owned:
    <li>${books_common.render_book(book)}</li>
  % endfor
</ol>

% if not username:
  <h3>Books you want!</h3>
% else:
  <h3>Books ${username} wants!</h3>
% endif

<ol>
  % for book in want:
    <li>${books_common.render_book(book)}</li>
  % endfor
</ol>

<%def name="title()">${parent.title()} - Home</%def>
