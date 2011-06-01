<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />

<ul id="have_list">
  % for have in events.have:
    <li>
      <div>${common.format_date_simple(have.date)}</div>
      <div class="front_page_cover">${common.book_cover(have.book)}</div>
      <div>
        ${common.user_link(have.owner)}
        has
        ${common.book_link(have.book, common.format_book_title(have.book))}
      </div>
      <div class="clear"></div>
    </li>
  % endfor
</ul>

<ul id="want_list">
  % for want in events.want:
    <li>
      <div>${common.format_date_simple(have.date)}</div>
      <div class="front_page_cover">${common.book_cover(want.book)}</div>
      <div>
        ${common.user_link(want.coveter)}
        wants
        ${common.book_link(want.book, common.format_book_title(want.book))}
      </div>
      <div class="clear"></div>
    </li>
  % endfor
</ul>

<ul id="exchange_list">
  % for exchange in events.exchange:
    <li>
      <div>${common.format_date_simple(have.date)}</div>
      <div class="front_page_cover">${common.book_cover(exchange.book)}</div>
      <div>
        ${common.user_link(exchange.giver)}
        gave
        ${common.user_link(exchange.taker)}
        ${common.book_link(exchange.book, common.format_book_title(exchange.book))}
      </div>
      <div class="clear"></div>
    </li>
  % endfor
</ul>


<%def name="title()">${parent.title()} - Home</%def>

