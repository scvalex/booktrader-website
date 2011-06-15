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

## -*- coding: utf-8 -*-

<%namespace name="common" file="/common.mak" />

<!DOCTYPE html>
<html>

  <head>

    <link rel="stylesheet"
          href="${request.static_url('booksexchange:static/css/reset.css')}"
          type="text/css" />

    <link href="${request.static_url('booksexchange:static/css/fonts.css')}"
          rel="stylesheet"
          type="text/css">

    <link rel="stylesheet"
          href="${request.static_url('booksexchange:static/css/style.css')}"
          type="text/css" />

    <script type="text/javascript"
            src="${request.static_url('deform:static/scripts/jquery-1.4.2.min.js')}">
    </script>

    <script type="text/javascript"
            src="${request.static_url('deform:static/scripts/deform.js')}">
    </script>


    ${self.head()}

    <title>${self.title()}</title>

  </head>

  <body>
    <div id="wrapper">

      <div id="header">
        <div id="user">
          % if request.user is not None:
              logged in as
              <a href="${request.resource_url(request.root['users'], 'cp')}">${request.user.username}</a>
              &middot;
              % if request.user.unread:
                <a class="unread" href="${request.resource_url(request.root['messages'], 'list')}">${len(request.user.unread)} unread</a>
              % else:
                <a href="${request.resource_url(request.root['messages'], 'list')}">inbox</a>
              % endif
              &middot;
              <a href="${request.resource_url(request.root['users'], 'logout')}">logout</a>
          % else:
              <a href="${request.resource_url(request.root['users'], 'login')}">login</a>
              &middot;
              <a href="${request.resource_url(request.root['users'], 'register')}">register</a>
          % endif
        </div>


        <h1><a href="${request.resource_url(request.root)}">BookTrader</a></h1>

      </div>

      <% flashes = request.session.pop_flash() %>
      % for flash in flashes:
          <div id="flash">${flash}</div>
      % endfor

      <div id="content">

        ${request.search_bar}


        <div id="inner">${next.body()}</div>

      </div>

      <div id="footer">
        ${self.footer()}

        <div class="footlinks">
          ·
          <a href="${request.resource_url(request.root, 'about')}">About ${title()}</a>
          ·
          <a href="${request.resource_url(request.root, 'about')}#authors">Contact</a>
          ·
          <a href="${request.resource_url(request.root, 'debug')}"><em>Debug info</em></a>
          ·
        </div>

      </div>

    </div>

    <script type="text/javascript">
      deform.load()
    </script>
  </body>
</html>



<%def name="title()">BookTrader</%def>

<%def name="heading()"></%def>

<%def name="head()">
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<link rel="shortcut icon" href="/favicon.ico" />
</%def>

<%def name="footer()"></%def>
