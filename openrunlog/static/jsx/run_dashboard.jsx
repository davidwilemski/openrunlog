/** @jsx React.DOM */
$(document).ready(function() {
    React.renderComponent(<RecentRuns url="/u/david/data/recent.json" />, document.getElementById('recentruns'));
});
