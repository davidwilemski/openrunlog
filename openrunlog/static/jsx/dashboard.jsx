/** @jsx React.DOM */

// Simple pure-React component so we don't have to remember
// Bootstrap's classes
var BootstrapButton = React.createClass({
  render: function() {
    // transferPropsTo() is smart enough to merge classes provided
    // to this component.
    return this.transferPropsTo(
      <a href={this.props.href} role="button" className={this.className} >
        {this.props.children}
      </a>
    );
  }
});

var BootstrapModal = React.createClass({
  // The following two methods are the only places we need to
  // integrate with Bootstrap or jQuery!
  componentDidMount: function() {
    // When the component is added, turn it into a modal
    $(this.getDOMNode())
      .modal({backdrop: 'static', keyboard: false, show: false});
  },
  componentWillUnmount: function() {
    $(this.getDOMNode()).off('hidden', this.handleHidden);
  },
  close: function() {
    $(this.getDOMNode()).modal('hide');
  },
  open: function() {
    $(this.getDOMNode()).modal('show');
  },
  render: function() {
    var confirmButton = null;
    var cancelButton = null;

    if (this.props.confirm) {
      confirmButton = (
        <BootstrapButton
          onClick={this.handleConfirm}
          id={this.props.confirmId} 
          className="btn btn-primary">
          {this.props.confirm}
        </BootstrapButton>
      );
    }
    if (this.props.cancel) {
      cancelButton = (
        <BootstrapButton className="btn btn-cancel" onClick={this.handleCancel}>
          {this.props.cancel}
        </BootstrapButton>
      );
    }

    return (
      <div className="modal fade" id={this.props.id} aria-hidden="true" role="dialog">
      <div className="modal-dialog">
      <div className="modal-content">
        <div className="modal-header">
          <button
            type="button"
            className="close"
            onClick={this.handleCancel}
            dangerouslySetInnerHTML={{__html: '&times'}}
          />
          <h3>{this.props.title}</h3>
        </div>
        <div className="modal-body">
          {this.props.children}
        </div>
        <div className="modal-footer">
          {cancelButton}
          {confirmButton}
        </div>
      </div>
      </div>
      </div>
    );
  },
  handleCancel: function() {
    if (this.props.onCancel) {
      this.props.onCancel();
    }
  },
  handleConfirm: function() {
    if (this.props.onConfirm) {
      this.props.onConfirm();
    }
  }
});

var DateInput = React.createClass({
  getDefaultProps: function() {
    return {value: (new Date()).toLocaleDateString("en-US"), error: false}
  },

  render: function() {
    var value = this.props.value;
    var div_classes = "form-group";
    var date_error_text = "Must be a valid date.";

    if (this.props.error) {
      div_classes += " has-error";
    }

    var form = (
      <div className={div_classes}>
        <label for="date">Date (MM/DD/YYYY)</label>
        <input className="form-control" type="text"
        name="date" id="date"
        value={value}
        onChange={this.props.onChange}
        data-required="true" />
        <label className="control-label" for="date"> {this.props.error ? date_error_text : ""} </label>
      </div>
    );

    return form;
  }
});

var PaceTimeInput = React.createClass({
  propTypes: {
    toggle: React.PropTypes.oneOf(["pace", "time"]),
    time: React.PropTypes.string,
  },

  getDefaultProps: function() {
    return {
      toggle: "time",
      time: "",
      error: false
    };
  },

  render: function() {
    var div_classes = "form-group";
    var pace_error_text = "HH:MM:SS, MM:SS, or MM formats only. Double check that you entered the correct time (we might have detected an impossibly fast pace).";

    if (this.props.error) {
      div_classes += " has-error";
    }

    var form = (
      <div className={div_classes}>
        <select value={this.props.toggle} onChange={this.props.onChange("toggle")}
        className="form-control" name="pacetime" id="pacetime">
          <option value="time">Time:</option>
          <option value="pace">Pace:</option>
        </select>
        <input className="form-control" type="text"
        name="time" 
        id="time" 
        placeholder={this.props.toggle === "time" ? "28:00" : "7:30"}
        value={this.props.time} onChange={this.props.onChange("time")}
        data-time 
        />
        <label className="control-label" for="time"> {this.props.error ? pace_error_text : ""} </label>
      </div>
    );

    return form;
  }
});

var DistanceInput = React.createClass({
  propTypes: {
    onChange: React.PropTypes.func.isRequired,
    distance: React.PropTypes.string
  },

  getDefaultProps: function() {
    return {distance: "", error: false};
  },

  // XXX not perfectly happy with displaying error by default but it's a start
  render: function() {
    var div_classes = "form-group";

    var distance_error_text = "Must be a number between 0 and 250.";

    if (this.props.error) {
      div_classes += " has-error"
    }

    var form = (
        <div className={div_classes}>
          <label for="distance">Distance (Miles)</label>
          <input className="form-control" type="text" name="distance" 
          value={this.props.distance} onChange={this.props.onChange}
          id="distance" placeholder="4" data-required="true" 
          data-min="0" data-max="250" data-type="number" />
          <label className="control-label" for="distance" >{this.props.error ? distance_error_text : ""} </label>
        </div>
    );

    return form;
  }
});

var NotesInput = React.createClass({
  propTypes: {
    value: React.PropTypes.string.isRequired
  },

  render: function() {
    var form = (
      <div className="form-group">
        <label for="notes">Notes:</label>
        <textarea className="form-control" 
        name="notes" id="notes" 
        placeholder="Thoughts about your run here" 
        data-regexp=".*" value={this.props.value} onChange={this.props.onChange} />
      </div>
    );

    return form;
  }
});

// TODO - make this a dynamic UI component that doesn't refresh the page on submit
var RunForm = React.createClass({
  propTypes: {
    date: React.PropTypes.string,
    distance: React.PropTypes.string,
    toggle: React.PropTypes.oneOf(['pace','time']),
    time: React.PropTypes.string,
  },

  getDefaultProps: function() {
    return {
      date: (new Date()).toLocaleDateString("en-US"),
      toggle: "time",
      time: "",
      distance: "",
      notes: ""
    }
  },

  getInitialState: function() {
    return {
      date: this.props.date,
      toggle: this.props.toggle,
      time: this.props.time,
      distance: this.props.distance,
      notes: this.props.notes
    }
  },

  handleChange: function(val) {
    var that = this;
    return function(event) {
      var state = {}
      state[val] = event.target.value;
      that.setState(state);
    }
  },

  ajaxSubmit: function(callback) {
    if (this.paceTimeIsValid(this.state.time) && 
        this.dateIsValid(this.state.date) && 
        this.distanceIsValid(this.state.distance)) {
      $.ajax({
        type: "POST",
        url: "/add",
        data: {
          date: this.state.date,
          distance: this.state.distance,
          time: this.state.time,
          pacetime: this.state.toggle,
          notes: this.state.notes
        },
        success: function(data) {
          callback({
            date: this.state.date,
            distance: this.state.distance,
            time: this.state.time,
            pacetime: this.state.toggle,
            notes: this.state.notes
          });
          this.setState(this.getInitialState());
          update_charts();
        }.bind(this)
      });
      return;
    }

    alert("Your run\'s information has some errors. Fix them and resubmit");
  },

  paceTimeIsValid: function(value) {
    var time = value;

    if (time === "") {
      return true
    }

    try {
      var secs = time_to_seconds(time);
    } catch(e) {
      return false;
    }

    if (time_to_seconds(time) < 0) {
      return false;
    }

    //TODO validate that pace doesn't seem impossibly fast

    return true;
  },

  distanceIsValid: function(value) {
    return (/^[0-9\.]+$/.test(value) && parseInt(value, 10) <= 250);
  },

  // XXX better than nothing, for now
  dateIsValid: function(value) {
    return /^[0-1]?[0-9]\/[0-3]?[0-9]\/[0-9]{4}$/g.test(value);
  },

  render: function() {
    var div_classes = "form-group";

    var isPaceTimeValid = this.paceTimeIsValid(this.state.time);
    var isDistanceValid = this.distanceIsValid(this.state.distance);
    var isDateValid = this.dateIsValid(this.state.date);

   var form = null;
    form = (
      <form id={this.props.id} method="POST" action="/add" 
      className="form-horizontal">

        <DateInput 
            error={!isDateValid ? true : false}
            value={this.state.date} onChange={this.handleChange("date")}/>

        <PaceTimeInput toggle={this.state.toggle} time={this.state.time}
            onChange={this.handleChange} error={!isPaceTimeValid ? true : false} />

        <DistanceInput distance={this.state.distance} 
            error={!isDistanceValid ? true : false}
            onChange={this.handleChange("distance")} />

        <NotesInput value={this.state.notes} onChange={this.handleChange("notes")} />
      </form>
    );
    return <span>{form}</span>;
  }
});


var AddRunModal = React.createClass({
  propTypes: {
    onSubmit: React.PropTypes.func.isRequired
  },

  handleCancel: function() {
    if (confirm('Are you sure you want to cancel?')) {
      this.refs.modal.close();
    }
  },

  render: function() {
    var modal = null;
    var submitbtnid = 'addrunbtn';

    modal = (
      <BootstrapModal
        ref="modal"
        id="addrun"
        confirm="Add Run"
        confirmId={submitbtnid}
        cancel="Cancel"
        onCancel={this.handleCancel}
        onConfirm={this.handleSubmit}
        title="Add A Run">
          <RunForm id="addrunform" ref="runform" />
      </BootstrapModal>
    );

    return (
      <div className="addrunmodal">
        {modal}
        <BootstrapButton href="javascript:;" onClick={this.openModal} className="label label-success">Add a run</BootstrapButton>
      </div>
    );
  },
  openModal: function() {
    this.refs.modal.open();
  },
  closeModal: function() {
    this.refs.modal.close();
  },
  handleSubmit: function() {
    this.refs.runform.ajaxSubmit(this.props.onSubmit);
    this.closeModal();
  }
});

var Run = React.createClass({
  propTypes: {
    run: React.PropTypes.object.isRequired
  },
  render: function() {
    var run = this.props.run;
    return <div key={run.id}><a href={run.uri}>{run.date} - {run.distance} Miles - {run.pace}</a></div>;
  }
});

var RunList = React.createClass({
  propTypes: {
    runs: React.PropTypes.array.isRequired
  },
  render: function() {
    var runNodes = null;
    runNodes = this.props.runs.map(function (run) {
      return <Run run={run} />
    });
    return <span>{runNodes}</span>;
  }

});

var RecentRuns = React.createClass({
  propTypes: {
    url: React.PropTypes.string.isRequired
  },

  fetchRuns: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data.data}); 
      }.bind(this)
    });
  },

  getInitialState: function() {
    return {data: []};
  },

  componentWillMount: function() {
    this.fetchRuns();
  },

  addRunToState: function(run) {
    this.fetchRuns();
  },

  render: function() {
    var addrunmodal = null;

    if (document.getElementById("addrun")) {
      addrunmodal = <AddRunModal onSubmit={this.addRunToState} />;
    }

    return ( 
      <div>
        <h2>Recent Runs:</h2>
        {addrunmodal}
        <RunList runs={this.state.data} />
      </div>
    );
  }
});
