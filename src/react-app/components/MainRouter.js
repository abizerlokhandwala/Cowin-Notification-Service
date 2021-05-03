import React from 'react'
import { Row } from 'antd'
import {
  Route,
  Switch
} from 'react-router-dom'

import Subscription from './subscription/index'
import PageNotFound from './common/error-pages/PageNotFound'
import Landing from './Landing'


function MainRouter () {
  return (
    <Route
      render={({ location }) => (
        <Row className='overflow-auto display-block'>
          <Switch location={location}>
            <Route path="/subscribe" component={Subscription} key="subscribe" />
            <Route path="/" component={Landing} key="landing" />
            <Route render={() => <PageNotFound />} key="notFound" />
          </Switch>
        </Row>
      )} />
  )
}

export default MainRouter
