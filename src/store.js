import { createStore, compose, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'
import logger from 'redux-logger'
import reducer from '../src/react-app/reducers/index'
import getMiddleware from './common/middlewares/getAPI'
import postMiddleware from './common/middlewares/postAPI'

const composeEnhances = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose

let store

if (process.env.NODE_ENV === 'development') {
  store = createStore(reducer, composeEnhances(
    applyMiddleware(thunk, getMiddleware, postMiddleware),
    applyMiddleware(logger)
  ))
} else {
  store = createStore(reducer, composeEnhances(
    applyMiddleware(thunk, getMiddleware, postMiddleware)
  ))
}

export default store
