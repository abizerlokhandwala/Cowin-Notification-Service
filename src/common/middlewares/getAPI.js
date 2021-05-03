import { camelCaseKeys } from '../utils'

// Fetches an API response and normalizes the result JSON according to schema.
// This makes every API response have the same shape, regardless of how nested it was.
function getApi (endpoint) {
  return fetch(endpoint, {
    credentials: 'same-origin'
  })
    .then(response => {
      return response.json().then(json => ({ json, response })).catch(() => {
        if (response.ok) {
          return Promise.resolve({ response })
        }
        // eslint-disable-next-line prefer-promise-reject-errors
        return Promise.reject({
          status: response.status
        })
      })
    }).then(({ json, response }) => {
      if (Array.isArray(json)) {
        json = {
          data: json
        }
      } else if (typeof json !== 'object') {
        json = {}
      }
      json.isServerOK = !!response.ok
      const camelizedJson = camelCaseKeys(json)
      if (!camelizedJson.isServerOK) {
        // eslint-disable-next-line prefer-promise-reject-errors
        return Promise.reject({
          status: response.status,
          ...camelizedJson
        })
      }
      return { ...camelizedJson }
    })
}

// Action key that carries API get info interpreted by this Redux middleware.
export const GET_API = Symbol('Get API')

// A Redux middleware that interprets actions with GET_API info specified.
// Performs the get and promises when such actions are dispatched.
export default store => next => action => {
  const getAPI = action[GET_API]
  if (typeof getAPI === 'undefined') {
    return next(action)
  }

  let { endpoint } = getAPI
  const { types } = getAPI

  if (typeof endpoint === 'function') {
    endpoint = endpoint(store.getState())
  }

  if (typeof endpoint !== 'string') {
    throw new Error('Specify a string endpoint URL.')
  }
  if (!Array.isArray(types) || types.length !== 3) {
    throw new Error('Expected an array of three action types.')
  }
  if (!types.every(type => typeof type === 'string')) {
    throw new Error('Expected action types to be strings.')
  }

  const [requestType, successType, failureType] = types

  function actionWith (data) {
    const finalAction = { ...action, ...data }
    delete finalAction[GET_API]
    return finalAction
  }

  function successHandler (response) {
    if (getAPI.successTypeActionProps) {
      next(actionWith({ response, ...getAPI.successTypeActionProps, type: successType }))
    } else {
      next(actionWith({ response, type: successType }))
    }
    const { onSuccess } = getAPI
    if (onSuccess) {
      if (typeof onSuccess !== 'function') {
        throw new Error('Success Callback should be a function')
      }
      onSuccess(response, store.getState(), store.dispatch)
    }
  }

  function handleGetApi () {
    return getApi(endpoint).then(successHandler, failureHandler)
  }

  function failureHandler (response) {
    response.status = response.status || 0

    next(actionWith({
      type: failureType,
      error: response.message || 'Something bad happened'
    }))

    const { onFailure } = getAPI

    if (onFailure) {
      if (typeof onFailure !== 'function') {
        throw new Error('Failure Callback should be a function')
      }
      onFailure(response, store.getState(), store.dispatch)
    }
  }

  let requestTypeActionData = { type: requestType }

  if (getAPI.requestTypeActionProps) {
    requestTypeActionData = { ...requestTypeActionData, ...getAPI.requestTypeActionProps }
  }
  next(actionWith(requestTypeActionData))
  return handleGetApi()
}
