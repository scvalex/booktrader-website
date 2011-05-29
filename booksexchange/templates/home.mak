<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />

<ul>
  % for have in events.have:
    <li>
      ${common.book_cover(have.book)} ${common.user_link(have.owner)} has ${common.book_link(have.book, common.format_book_title(have.book))}
    </li>
  % endfor
</ul>

<ul>
  % for want in events.want:
    <li>
      ${common.book_cover(want.book)} ${common.user_link(want.coveter)} wants ${common.book_link(want.book, common.format_book_title(want.book))}
    </li>
  % endfor
</ul>

<ul>
  % for exchange in events.exchange:
    <li>
      ${common.book_cover(exchange.book)} ${common.user_link(exchange.giver)} gave ${common.user_link(exchange.taker)} ${common.book_link(exchange.book, common.format_book_title(exchange.book))}
    </li>
  % endfor
</ul>


<%def name="title()">${parent.title()} - Home</%def>

