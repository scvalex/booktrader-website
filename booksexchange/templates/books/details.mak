<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

<h3>${book.title}</h3>

${books_common.render_book(book)}

<%def name="title()">${parent.title()} - Details</%def>
