import React from 'react'
import { Row, Col, Button } from 'antd'
import { TableOutlined } from '@ant-design/icons'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import Loader from './common/Loader'

import cowinLogo from '../../assets/images/cowin-notification-system-logo.png'

class BaseContent extends React.Component {
  render() {
    return (
      <Row className='padding--sides width-100 height-100 background-white'>
        <Col span={24} className='center' >
          <img src={cowinLogo} alt='cowin-notification-system-logo' height={200} />
          <Loader />
          <div>
            <Link to='/subscribe'>
              <Button type="primary" className='margin-half--ends margin--sides background-green on-hover-light' style={{border: 0 }} shape="round" icon={<TableOutlined />}>
                Subscribe here!
              </Button>
            </Link>
          </div>
        </Col>
      </Row>
    )
  }
}

BaseContent.propTypes = {
  base: PropTypes.object.isRequired,
}

const mapStateToProps = ({ base }) => {
  return {
    base
  }
}

export default connect(
  mapStateToProps, {
})(BaseContent)
