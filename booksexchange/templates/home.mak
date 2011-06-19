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
    <div class="step">Profit!</div>
  </div>

  <div id="website">
    This is the website
  </div>

  <div id="android">
    We also have a cute droid
  </div>

  <div id="iphone">
    And a cute iphone
  </div>
</div>

<div id="stuff_in_flux">
  ${common.render_events(events.all[:10])}
</div>

<%def name="title()">${parent.title()} - Home</%def>

