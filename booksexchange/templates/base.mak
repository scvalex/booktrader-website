## -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml">

  <head>

    <script type="text/javascript" src="${request.static_url('deform:static/scripts/deform.js')}"></script>

    <link rel="stylesheet" href="${request.static_url('deform:static/css/form.css')}" type="text/css" />
    <link rel="stylesheet" href="${request.static_url('deform:static/css/theme.css')}" type="text/css" />

    ${self.head()}

    <title>${self.title()}</title>

  </head>

  <body>
    
    <h1>BooksExchange</h1>

    <% flashes = request.session.pop_flash() %>
    % for flash in flashes:
        <div id="flash">
          <span class="message">${flash}</span>
        </div>
    % endfor

    ${next.body()}

    <div id="footer">${self.footer()}</div>
  </body>
</html>



<%def name="title()">BooksExchange</%def>

<%def name="heading()"></%def>

<%def name="head()">
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<link rel="shortcut icon" href="/favicon.ico" />
</%def>

<%def name="footer()"></%def>
