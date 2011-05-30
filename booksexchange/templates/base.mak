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
              logged in as ${common.user_link(request.user)}
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


        <h1><a href="${request.resource_url(request.root)}">BooksExchange</a></h1>

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
        foot foot foot
        ${self.footer()}
      </div>

    </div>

    <script type="text/javascript">
      deform.load()
    </script>
  </body>
</html>



<%def name="title()">BooksExchange</%def>

<%def name="heading()"></%def>

<%def name="head()">
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<link rel="shortcut icon" href="/favicon.ico" />
</%def>

<%def name="footer()"></%def>
