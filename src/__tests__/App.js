import React from 'react'
import { shallow } from 'enzyme'
import { Provider } from 'react-redux'
import App from '../App'
import store from '../store'

it('renders without crashing', () => {
  shallow((
    <Provider store={store}>
      <App />
    </Provider>
  ))
})
