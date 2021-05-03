import React from "react";
import { connect } from 'react-redux';
import PropTypes from 'prop-types'


class Subscription extends React.Component {

 

  render() {

    return (
      <div>
        
      </div>
    );
  }
}

const mapStateToProps = ({ base }) => {
  const {
    subscription = {}
  } = base
  return {
    subscription
  }
}

Subscription.propTypes = {
  subscription: PropTypes.object.isRequired,
}

export default connect(
  mapStateToProps, {})(Subscription)

