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

