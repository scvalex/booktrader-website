<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />
<%namespace name="books_common" file="/books/common.mak" />

${books_common.render_book(book)}

<div id="owners_list">
  <h3>Owners</h3>
  % if book.owners:
    <ul>
      % for user in book.owners.values():
        <li>
          ${common.gravatar(user)}
          <a href="${request.resource_url(user, book.identifier, 'offer')}"
             class="blue_button">
            Make offer
          </a>
        </li>
      % endfor
    </ul>
  % else:
    <div class="bad_news">No one owns this book :|</div>
  % endif
</div>

<div id="coveters_list">
  <h3>Coveters</h3>
  % if book.coveters:
    <ul>
      % for user in book.coveters.values():
        <li>${common.gravatar(user)}</li>
      % endfor
    </ul>
  % else:
    <div class="bad_news">No one wants this book ;(</div>
  % endif
</div>

<%def name="title()">${parent.title()} - Details</%def>
