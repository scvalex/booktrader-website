<%inherit file="/base.mak"/>
<p>
  Login:
</p>
<form method="POST" action="${request.path_url}">
  <input type="hidden" name="came_from" value="${came_from}" />
  
  <label for="username">Username</label>
  <input type="text" name="username" value="${username}" /><br/>
  
  <label for="password">Password</label>
  <input type="password" name="password" /><br/>
  
  <input type="submit" name="form.submitted" value="Log In" />
</form>

<%def name="title()">${parent.title()} - Home</%def>
