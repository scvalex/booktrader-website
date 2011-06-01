<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />
<%namespace name="books_common" file="/books/common.mak" />

${books_common.render_book(book)}

<div>
  <h3>Owners:</h3>
  <ul>
  % for user in book.owners.values():
    <li>${common.user_link(user)}</li>
  % endfor
  </ul>
</div>

<div>
  <h3>Coveters:</h3>
  <ul>
  % for user in book.coveters.values():
    <li>${common.user_link(user)}</li>
  % endfor
  </ul>
</div>

<%def name="title()">${parent.title()} - Details</%def>
