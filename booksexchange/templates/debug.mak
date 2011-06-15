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
