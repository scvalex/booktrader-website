<%inherit file="/base.mak"/>

<%namespace name="common" file="/common.mak" />

${common.render_events(events.all)}

<%def name="title()">${parent.title()} - Home</%def>

