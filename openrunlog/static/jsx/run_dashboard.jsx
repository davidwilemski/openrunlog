/** @jsx React.DOM */
$(document).ready(function() {
    var uri = window.location.pathname;
    React.renderComponent(<RecentRuns url={ uri + "/data/recent.json" } />, document.getElementById('recentruns'));
});
