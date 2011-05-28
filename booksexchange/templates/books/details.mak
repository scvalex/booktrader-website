<%inherit file="/base.mak"/>

<%namespace name="common" file="/books/common.mak" />

<h3>${book.title}</h3>

${common.render_book(book)}

<%def name="title()">${parent.title()} - Details</%def>
