<%inherit file="/base.mak"/>

<%namespace name="common" file="/books/common.mak" />

<h3>Your books!</h3>

<ol>
  % for book in owned:
    <li>${common.render_book(book)}</li>
  % endfor
</ol>

<h3>Books you want!</h3>

<ol>
  % for book in want:
    <li>${common.render_book(book)}</li>
  % endfor
</ol>

<%def name="title()">${parent.title()} - List</%def>
