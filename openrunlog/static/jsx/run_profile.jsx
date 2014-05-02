/** @jsx React.DOM */
$(document).ready(function() {
  var uri = window.location.pathname;
  var user_uri = uri.split("/").slice(0, 3).join("/");

  $.get(user_uri + "/data/profile.json", function(data) {
    React.renderComponent(
      <ProfileSidebar profile={data} />,
      document.getElementById("profile-display"));
  });
});
