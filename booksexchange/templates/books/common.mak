<%namespace name="common" file="/common.mak" />

<%def name="render_book_short(book)">
  <div class="book_short">
    <div class="cover">
      ${common.book_link(book, common.book_cover(book))}
    </div>

    <h3>${common.book_link(book, book.title)}</h3>

    % if book.authors:
        <p class="authors">
          by ${', '.join(['<span class="author">' + author + '</span>'
                          for author in book.authors])}
        </p>
    % endif

    % if book.description:
        <p>${common.truncate(book.description, 200)}</p>
    % endif

    <div class="have_want">
      % if request.user and book.identifier in request.user.owned:
        <span>You have this book.</span>
      % elif request.user and book.identifier in request.user.want:
        <span>You want this book.</span>
      % else:
        <a href="${request.resource_url(book, 'have')}">Have</a>
        <a href="${request.resource_url(book, 'want')}">Want</a>
      % endif
    </div>
  </div>
</%def>

<%def name="books_list(books)">
  <table class="books_list" style="border-spacing: 10px;">
    <% books.reverse() %>
    % while len(books) > 1:
        <tr>
          <td>${render_book_short(books.pop())}</td>
          <td>${render_book_short(books.pop())}</td>
        </tr>
    % endwhile
    % if len(books) > 0:
        <tr>
          <td>${render_book_short(books.pop())}</td>
          <td class="blank"></td>
        </tr>
    % endif
  </table>
</%def>

<%def name="render_book(book)">
  <div class="book_details">
    <div class="cover">
      ${common.book_link(book, common.book_cover(book))}

    </div>

    % if len(book.owners) > 0:
        <div class="owners">
          <span>Owners:</span><br/>
          <ul>
            % for u in book.owners.values():
                <li>${common.user_link(u)}</li>
            % endfor
          </ul>
        </div>
    % endif
    % if len(book.coveters) > 0:
        <div class="coveters">
          <span>Coveters:</span><br/>
          <ul>
            % for u in book.coveters.values():
                <li>${common.user_link(u)}</li>
            % endfor
          </ul>
        </div>
    % endif


    <h2>${common.book_link(book, book.title)}</h2>
    % if book.subtitle:
        <h3>${book.subtitle}</h3>
    % endif

    % if book.authors:
        <p class="authors">
          by ${', '.join(['<span class="author">' + author + '</span>'
                          for author in book.authors])}
        </p>
    % endif

    <ul class="book_info">
      ${maybe_li(book.publisher)}
      ${maybe_li(book.year)}

      % for ident in book.identifiers:
          <li class="book_identifier">${ident[0]}: ${ident[1]}</li>
      % endfor
    </ul>

    % if book.description:
        <p>${book.description}</p>
    % endif
    
    <div class="have_want">
      % if request.user and book.identifier in request.user.owned:
          <span>You have this book.</span>
      % elif request.user and book.identifier in request.user.want:
          <span>You want this book.</span>
      % else:
          <a href="${request.resource_url(book, 'have', book.identifier)}">Have</a>
          <a href="${request.resource_url(book, 'want', book.identifier)}">Want</a>
      % endif
    </div>
  </div>
</%def>

<%def name="maybe_li(x)">
  % if x:
    <li>${x}</li>
  % endif
</%def>
