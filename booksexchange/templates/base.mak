## -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml">

  <head>

    <link rel="stylesheet"
          href="${request.static_url('booksexchange:static/css/reset.css')}"
          type="text/css" />

    <link href="http://fonts.googleapis.com/css?family=Cabin:regular,regularitalic,bold"
          rel="stylesheet"
          type="text/css">
    
    <link rel="stylesheet"
          href="${request.static_url('deform:static/css/form.css')}"
          type="text/css" />
    
    <link rel="stylesheet"
          href="${request.static_url('booksexchange:static/css/style.css')}"
          type="text/css" />
    
    ${self.head()}

    <title>${self.title()}</title>

  </head>

  <body>
    <div id="wrapper">

      <div id="header">
        <div id="user">
          login register etc
        </div>

        <h1><a href="${request.resource_url(request.root)}">BooksExchange</a></h1>
      </div>

      <div id="menu">
        menu
      </div>
      
      <div id="searchbar">
        searchbar
      </div>
      
      
      <% flashes = request.session.pop_flash() %>
      % for flash in flashes:
          <div id="flash">${flash}</div>
      % endfor

      ${next.body()}

      <div id="footer">${self.footer()}</div>

    </div>
  </body>
</html>



<%def name="title()">BooksExchange</%def>

<%def name="heading()"></%def>

<%def name="head()">
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<link rel="shortcut icon" href="/favicon.ico" />
</%def>

<%def name="footer()"></%def>
