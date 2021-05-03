import React from 'react'
import { Link } from 'react-router-dom'
import { Row, Col, Button } from 'antd'

const PageNotFound = () => {
  return (
    <Row style={{ marginTop: 60, textAlign: 'center', width: '100%' }}>
      <Col span={12} offset={6} >
        <h1 className='f48'> 404 </h1>
        <h2 className='f36'> PAGE NOT FOUND </h2>
        <h3 className='text-light-grey'> &quot; Not all those who wander are lost &quot; </h3>
        <Button type='primary'>
          <Link to="/"> Go to Homepage </Link>
        </Button>
      </Col>
    </Row>
  )
}

export default PageNotFound
