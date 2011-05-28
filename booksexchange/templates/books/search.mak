<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

<h3>Find books!</h3>

<ul>
  % for book in result:
    <li>
      ${books_common.render_book(book)}
      <div>
        <a href="${request.resource_url(request.context, 'add', 'have', book.identifier)}">Have</a>
        <a href="${request.resource_url(request.context, 'add', 'want', book.identifier)}">Want</a>
      </div>
    </li>
  % endfor
</ul>

<%def name="title()">${parent.title()} - Search</%def>
