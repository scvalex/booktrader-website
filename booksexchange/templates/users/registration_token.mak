<%inherit file="/base.mak"/>
<h2>Register</h2>

<p>
  % if not wrong_token:
      A verification token has been generated, 
  % else:
      We are sorry, but the verification token is wrong. <br/>
      A new one has been generated, 
  % endif
  please check your email to activate your account.
</p>

<%def name="title()">${parent.title()} - Register</%def>
