<%inherit file="/base.mak"/>

<%namespace name="common" file="/books/common.mak" />

<h3>Find books!</h3>

${form}

<ol>
  % for book in result:
    <li>
      ${common.render_book(book)}
      <div>
        <a href="${request.resource_url(request.context, 'add', book.googleId)}">
          Have
        </a>
      </div>
    </li>
  % endfor
</ol>

<%def name="title()">${parent.title()} - Search</%def>
