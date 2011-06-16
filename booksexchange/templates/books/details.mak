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
