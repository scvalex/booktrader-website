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

<h2>About ${parent.title()}</h2>

<div style="width: 45%; padding-right: 4%; float: left;">
  <a name="license"></a>
  <div class="aboutbox">
    <h3>License</h3>

    <p>
      <img alt="GNU AGPL v3 logo" src="${request.static_url('booksexchange:static/img/agplv3-155x51.png')}" />
      <br>
      ${parent.title()} is licensed under the terms of the
        <a href="${request.static_url('booksexchange:static/agpl-3.0.txt')}">GNU AGPL version 3</a>
      .
    </p>
  </div>


  <a name="technology"></a>
  <div class="aboutbox">
    <h3>Technology and Open Source</h3>

    <p>${parent.title()} would not exist without the following open source projects:</p>

    <ul class="abouttech">
      <li class="techitem">
        <h4>Python</h4>

        <p><a href="http://python.org/">
          <img alt="Python Logo" src="${request.static_url('booksexchange:static/img/python-logo.gif')}" />
        </a></p>
      </li>

      <li class="techitem">
        <h4>Pyramid</h4>

        <p><a href="http://pylonsproject.org/">
          <img alt="Pyramid Logo" src="${request.static_url('booksexchange:static/img/pyramid-small.png')}" />
        </a></p>
      </li>

      <li class="techitem">
        <h4>Repoze</h4>

        <p><a href="http://repoze.org/">
          <img alt="Repoze Logo" src="${request.static_url('booksexchange:static/img/repoze-logo_lo.gif')}" />
        </a></p>
      </li>

      <li class="techitem">
        <h4>Zope</h4>

        <p><a href="http://www.zope.org/">
          <img alt="Zope Logo" src="${request.static_url('booksexchange:static/img/zope-logo.gif')}" />
        </a></p>
      </li>
    </ul>
  </div>
</div>



<div style="width: 45%; padding-right: 4%; float: left;">
  <a name="compliance"></a>
  <div class="aboutbox">
    <h3>Compliance</h3>

    <p>The ${parent.title()} web interface makes use of HTML 5 and CSS 3.</p>

    <p><a href="http://www.w3.org/html/logo/">
      <img alt="HTML5 Logo" src="${request.static_url('booksexchange:static/img/html5-badge-h-css3.png')}" />
    </a></p>

  </div>



  <a name="authors"></a>
  <div class="aboutbox">
    <h3>Authors</h3>

    <p>${parent.title()} is brought to you by:</p>
    <ul class="authors">
      <li>
        <a href="http://mazzo.li/">Francesco Mazzoli</a>
      </li>

      <li>
        <a href="http://www.abstractbinary.org/">Alexandru Scvortov</a>
      </li>

      <li>
        Ingrid Funie
      </li>

      <li>
        Max Staudt
      </li>
    </ul>
  </div>
</div>

<%def name="title()">About</%def>
