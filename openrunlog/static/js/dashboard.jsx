/** @jsx React.DOM */

// Simple pure-React component so we don't have to remember
// Bootstrap's classes
var BootstrapButton = React.createClass({
  render: function() {
    // transferPropsTo() is smart enough to merge classes provided
    // to this component.
    console.log(this);
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
      .modal({backdrop: 'static', keyboard: false, show: false})
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

  getInitialState: function() {
    return {
      value: (new Date()).toLocaleDateString("en-US")
    };
  },

  handleChange: function(event) {
    //TODO validate date here
    this.setState({value: event.target.value});
  },

  render: function() {
    var value = this.state.value;

    var form = (
      <div className="form-group">
        <label for="date">Date (MM/DD/YY)</label>
        <input className="form-control" type="text"
        name="date" id="date"
        value={value}
        onChange={this.handleChange}
        data-required="true" />
      </div>
    );

    return form;
  }
});

var PaceTimeInput = React.createClass({
  getInitialState: function() {
    return {
      value: "time" 
    };
  },

  handleChange: function(event) {
    this.setState({value: event.target.value});
  },

  render: function() {
    var form = (
      <div className="form-group">
        <select value={this.state.value} 
        className="form-control" name="pacetime" id="pacetime">
          <option value="time">Time:</option>
          <option value="pace">Pace:</option>
        </select>
        <input className="form-control" type="text"
        name="time" 
        id="time" 
        placeholder="28:00" data-time 
        />
      </div>
    );

    return form;
  }
});

var DistanceInput = React.createClass({
  getInitialState: function() {
    return {
      value: "" 
    };
  },

  handleChange: function(event) {
    //TODO validate time here
    this.setState({value: event.target.value});
  },

  render: function() {
    var form = (
        <div className="form-group">
          <label for="distance">Distance (Miles)</label>
          <input className="form-control" type="text" name="distance" 
          id="distance" placeholder="4" data-required="true" 
          data-min="0" data-max="250" data-type="number" />
        </div>
    );

    return form;
  }
});

var NotesInput = React.createClass({

  render: function() {
    var form = (
      <div className="form-group">
        <label for="notes">Notes:</label>
        <textarea className="form-control" 
        name="notes" id="notes" 
        placeholder="Thoughts about your run here" 
        data-regexp=".*"></textarea>
      </div>
    );

    return form;
  }
});

// TODO - refactor to have *Input value properties flow from a single source 
// TODO - make this a dynamic UI component that doesn't refresh the page on submit
var RunForm = React.createClass({
  componentDidMount: function(node) {
        // TODO - use react's built in validation?
        $('#' + this.props.id).parsley({
            trigger: 'change',
            successClass: 'success',
            errorClass: 'error',
            validationMinlength: '1',
            errors: {
                classHandler: function(elem) {
                    return $(elem).parents('div.control-group').first();
                },
                errorsWrapper: '<span class="help-inline"></span>',
                errorElem: '<span></span>',
            },
            validators: {
                time: function(val) {
                    // don't do this validation if entering pace
                    if($('#pacetime')[0].value === 'pace') {
                        return true;
                    }

                    // allow not posting time :/
                    if (val === '' || val == 0) {
                        return true;
                    }
                    
                    var time = /^((\d+:\d\d:\d\d$)|(\d+:\d\d$)|(\d+$))/m;
                    var timetest = time.test(val);
                    if(!timetest) {
                        return false;
                    }

                    var distance = parseInt($("#distance")[0].value, 10);
                    var seconds = time_to_seconds($("#time")[0].value);

                    if(seconds/distance < 200) {
                        return false;
                    }

                    return true;
                }
            },
            messages: {
                time: "HH:MM:SS, MM:SS, or MM formats only. Double check that you entered the correct time (we might have detected an impossibly fast pace)."
            }

        });
  },

  render: function() {
    var form = null;
    form = (
      <form id={this.props.id} method="POST" action="/add" 
      className="form-horizontal">
        <DateInput />
        <PaceTimeInput />
        <DistanceInput />
        <NotesInput />
      </form>
    );
    return <span>{form}</span>;
  }
});


var AddRunModal = React.createClass({
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
        onConfirm={this.submitModal}
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
  submitModal: function() {
    if ($("#addrunbtn").parsley('validate')) {
      document.getElementById("addrunform").submit();
      return;
    }

    alert("Your run\'s information has some errors. Fix them and resubmit");
  }
});

React.renderComponent(<AddRunModal/>, document.getElementById('addrun'));
