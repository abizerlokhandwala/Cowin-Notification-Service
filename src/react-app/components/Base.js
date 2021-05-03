import React from 'react'
import { Layout } from 'antd'

import MainRouter from './MainRouter'

const { Content } = Layout

function Base () {
  return (
    <Layout className='height-min-100'>
      <Content theme='light' className='height-min-100'>
        <MainRouter />
      </Content>
    </Layout>
  )
}

export default Base
