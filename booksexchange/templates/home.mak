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

<ul id="have_list">
  % for have in events.have:
    <li>
      ${common.render_event(have)}
      <div class="clear"></div>
    </li>
  % endfor
</ul>

<ul id="want_list">
  % for want in events.want:
    <li>
      ${common.render_event(want)}
      <div class="clear"></div>
    </li>
  % endfor
</ul>

<ul id="exchange_list">
  % for exchange in events.exchange:
    <li>
      ${common.render_event(exchange)}
      <div class="clear"></div>
    </li>
  % endfor
</ul>


<%def name="title()">${parent.title()} - Home</%def>

