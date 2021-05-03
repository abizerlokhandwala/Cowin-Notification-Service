import React from "react";
import PropTypes from 'prop-types'

class SubscriptionCard extends React.Component {


  render() {
    const {
      state,
      district,
      vaccineType,
      vaccineAgeGroup,
    } = this.props.subscription;

    return (
      <div>
        
      </div>
    );
  }
}

SubscriptionCard.propTypes = {
  subscription: PropTypes.object.isRequired,
}

export default SubscriptionCard
