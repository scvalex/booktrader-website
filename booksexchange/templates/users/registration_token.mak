<%inherit file="/base.mak"/>
<p>
  % if not wrong_token:
      A verification token has been generated, 
  % else:
      We are sorry, but the verification token is wrong. <br/>
      A new one has been generated, 
  % endif
  please check your email to activate your account.
</p>
