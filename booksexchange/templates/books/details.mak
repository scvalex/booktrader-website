<%inherit file="/base.mak"/>

<%namespace name="books_common" file="/books/common.mak" />

${books_common.render_book(book)}

<%def name="title()">${parent.title()} - Details</%def>
