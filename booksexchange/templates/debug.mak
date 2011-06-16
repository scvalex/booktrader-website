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

<h2>Debugging information</h2>

<div class="aboutbox">
  <h3>Sub-database versions</h3>

  <div style="padding-left: 1em;">
  <table>
    <tr><td>Users: </td><td>${str(request.root['users'].evolved)}</td></tr>
    <tr><td>Books: </td><td>${str(request.root['books'].evolved)}</td></tr>
    <tr><td>Events: </td><td>${str(request.root['events'].evolved)}</td></tr>
    <tr><td>Groups: </td><td>${str(request.root['groups'].evolved)}</td></tr>
    <tr><td>Messages: </td><td>${str(request.root['messages'].evolved)}</td></tr>
    <tr><td>Cache: </td><td>${str(request.root['cache'].evolved)}</td></tr>
  </table>
  </div>
</div>

<%def name="title()">About</%def>
