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

<div id="real_stuff">
  <div id="welcome">
    <h2>Welcome to BookTrader</h2>
    <p>Here you can trade your books for fun and profit.</p>
    <div class="count">1.</div>
    <div class="step">Find books you own and want</div>
    <div class="count">2.</div>
    <div class="step">We match you with traders</div>
    <div class="count">3.</div>
    <div class="step">...</div>
    <div class="count">4.</div>
    <div class="step last_step">Profit!</div>
  </div>

  <div id="website">
    <h3>Self-Ref FTW!</h3>
    <img src="${request.static_url('booksexchange:static/img/website_sshot.png')}"
         alt="Website screnshot" />
  </div>

  <div id="android">
    <h3>Android Inside</h3>
    <img src="${request.static_url('booksexchange:static/img/android_sshot.png')}"
         alt="Android screenshot" />
  </div>

  <div id="iphone">
    <h3>iPhone Friendly</h3>
    <img src="${request.static_url('booksexchange:static/img/iphone_sshot.png')}"
         alt="iPhone screenshot" />
  </div>
</div>

<div id="stuff_in_flux">
  ${common.render_events(events.all[:10])}
</div>

<%def name="title()">${parent.title()} - Home</%def>

<%def name="add_copyright()">
  <p>The Android Robot is reproduced from work created and <a href="http://code.google.com/policies.html">shared by Google</a> and used according to terms described in the <a href="http://creativecommons.org/licenses/by/3.0/">Creative Commons 3.0 Attribution License</a>.</p>
</%def>

