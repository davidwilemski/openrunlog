/** @jsx React.DOM */

var ProfileSidebar = React.createClass({
    render: function() {
        var profile = this.props.profile;
        var streaks = null;
        
        if (profile.streaks) {
            var mystreaks = profile.streaks;
            streaks = (<span>
                <div>Longest Streak: {mystreaks.longest.length} days</div>
                <div><small>{mystreaks.longest.start} - {mystreaks.longest.end}</small></div>
                <div>Current Streak: {mystreaks.current.length} days</div>
                <div><small>{mystreaks.current.start} - {mystreaks.current.end}</small></div>
            </span>);
        }
        
        return (<div>
            <a href={ profile.uri }>
                <img src={ profile.photo_url } />
                <h1>{ profile.display_name }</h1>
            </a>
            <p><strong>{ profile.hashtags.join(' ') }</strong></p>
            <div>
                All Time: { profile.total_mileage.toFixed(2) } Miles<br />
                2014: { profile.yearly_mileage.toFixed(2) } Miles<br />
                Past 7 Days: { profile.seven_days_mileage.toFixed(2) } Miles
            </div>
            {streaks}
        </div>);
    }
});

//$(document).ready(function() {
  var uri = window.location.pathname;
  var user_uri = uri.split("/").slice(0, 3).join("/");

  $.get(user_uri + "/data/profile.json", function(data) {
    React.renderComponent(
      <ProfileSidebar profile={data} />,
      document.getElementById("profile-display"));
  });
//});
