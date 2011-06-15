<%inherit file="/base.mak"/>

<h2>About ${parent.title()}</h2>


<a name="license"></a>
<div class="aboutbox">
  <h3>License</h3>

  <p>
    ${parent.title()} is licensed under the terms of the
      <a href="${request.static_url('booksexchange:static/gpl-3.0.txt')}">GNU GPL version 3</a>
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
  <h3>Authors and related projects</h3>

  <p>${parent.title()} is brought to you by:</p>
  <ul class="authors">
    <li>
      Francesco Mazzoli <a href="http://mazzo.li/">[mazzo.li]</a>
    </li>

    <li>
      Alexandru Scvortov <a href="http://www.abstractbinary.org/">[www.abstractbinary.org]</a>
    </li>

    <li>
      Ingrid Funie
    </li>

    <li>
      Max Staudt
    </li>
  </ul>
</div>


<%def name="title()">About</%def>
