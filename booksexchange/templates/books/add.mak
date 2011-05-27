<%inherit file="/base.mak"/>

% if status == 'ok':
  <h3>Book added!</h3>
% endif

See your bookshelf <a href="/books/owned">here</a>.

<%def name="title()">${parent.title()} - Search</%def>
