## Copyright 2011 the authors of BookTrader (see the AUTHORS file included).
##
## This file is part of BookTrader.
##
## BookTrader is free software: you can redistribute it and/or modify it
## under the terms of the GNU Affero General Public License as published
## by the Free Software Foundation, version 3 of the License.
##
## BookTrader is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even any implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## Affero General Public License version 3 for more details.
##
## You should have received a copy of the GNU Affero General Public
## License version 3 along with BookTrader. If not, see:
## http://www.gnu.org/licenses/

<%namespace name="common" file="/common.mak" />

<%def name="render_book_short(book, user = None, show_have_want = True)">
  <div class="book_short">
    <div class="cover">
      ${common.book_link(book, common.book_cover(book), user)}
    </div>

    <h3>${common.book_link(book, book.title, user)}</h3>


    % if book.authors:
        <p class="authors">
          by ${common.commify(book.authors,
                              lambda a: request.literal('<span class="author">' + a + '</span>'))}
        </p>
    % endif

    % if book.description:
        ${request.markdown(book.description[:150] + "...", safe_mode=False)}</div>
    % endif

    % if show_have_want:
      ${have_want(book)}
    % endif
  </div>
</%def>

<%def name="books_list(books, user = None)">
  <table class="books_list">
    <% books.reverse() %>
    % while len(books) > 1:
        <tr>
          <td>
            <% book = books.pop() %>
            ${list_owners(book)}
            ${render_book_short(book, user)}
          </td>
          <td>
            <% book = books.pop() %>
            ${list_owners(book)}
            ${render_book_short(book, user)}
          </td>
        </tr>
    % endwhile
    % if len(books) > 0:
        <tr>
          <td>
            <% book = books.pop() %>
            ${list_owners(book)}
            ${render_book_short(book, user)}
          </td>
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

    <h2>${common.book_link(book, book.title)}</h2>
    % if book.subtitle:
        <h3>${book.subtitle}</h3>
    % endif

    % if book.authors:
        <p class="authors">
          by ${common.commify(book.authors,
                              lambda a: request.literal('<span class="author">' + a + '</span>'))}
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
        ${request.markdown(book.description, safe_mode=False)}</p>
    % endif

    ${have_want(book)}
  </div>
</%def>

<%def name="maybe_li(x)">
  % if x:
    <li>${x}</li>
  % endif
</%def>

<%def name="have_want(book)">
  <div class="have_want">
    % if request.user and book.identifier in request.user.owned:
      <span>You have this book</span>
      <a href="${request.resource_url(book, 'remove')}" class="remove_book">✖</a>
    % elif request.user and book.identifier in request.user.want:
      <a href="${request.resource_url(book, 'have')}">Have</a>
      <span>You want this book</span>
      <a href="${request.resource_url(book, 'remove')}" class="remove_book">✖</a>
    % else:
      <a href="${request.resource_url(book, 'have')}">Have</a>
      <a href="${request.resource_url(book, 'want')}">Want</a>
    % endif
  </div>
</%def>

<%def name="list_owners(book)">
    <%
    from random import shuffle
    owners = book.owners.values()
    shuffle(owners)
    display = owners[:3]
    rest = owners [3:]
    %>

    % if display:
        <div class="owners">
          <span>Owners:</span>
          <ul>
            % for u in display:
                <li>
                  ${common.gravatar(u)}
                </li>
            % endfor
         </ul>
          % if len(rest) == 1:
              <span> and 1 other.</span>
          % elif len(rest) > 1:
              <span> and ${len(rest)} others.</span>
          % endif
        </div>
    % endif
</%def>

<%def name="owners_coveters(book)">

      <div class="owners">
        <span>Owners:</span><br/>
        <ul>
          % for u in book.owners.values():
              <li>
                <a href="${request.resource_url(u)}">
                  <img src="${u.gravatar(32)}" alt="${u.username}"/>
                  <span>${u.username}</span>
                </a>
              </li>
          % endfor
        </ul>
      </div>
      <div class="coveters">
        <span>Coveters:</span><br/>
        <ul>
          % for u in book.coveters.values():
              <li>
                <a href="${request.resource_url(u)}">
                  <img src="${u.gravatar(32)}" alt="${u.username}"/>
                  <span>${u.username}</span>
                </a>
              </li>
          % endfor
        </ul>
      </div>
</%def>

<%def name="paginate_url(i, books_per_page)">
<%
import urllib
query = request.GET
query['start_index'] = str(i * books_per_page)

return request.path + '?' + urllib.urlencode(query)
%>
</%def>
