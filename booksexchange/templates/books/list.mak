<%inherit file="/base.mak"/>

<%namespace name="common" file="/books/common.mak" />

<h3>Your books!</h3>

<ol>
  % for book in books:
    <li>${common.render_book(book)}</li>
  % endfor
</ol>

<%def name="title()">${parent.title()} - List</%def>
