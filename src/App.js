import './App.css'

import React from 'react'

import {
  BrowserRouter as Router,
  Route,
  Switch
} from 'react-router-dom'
import Base from './react-app/components/Base'


const App = () => (
  <Router>
    <div className='height-100'>
      <Switch>
        <Route path="/" component={Base} />
      </Switch>
    </div>
  </Router>
)

export default App
