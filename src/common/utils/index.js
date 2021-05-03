export const camelCaseKeys = (data) => {
  if (Array.isArray(data)) {
    return camelCaseKeysInArray(data)
  }

  const nestedCamelCasedData = Object.keys(data).reduce((config, datum) => {
    if (Array.isArray(data[datum])) {
      config[datum] = camelCaseKeysInArray(data[datum])
    } else {
      config[datum] = camelCaseKeysInObject(data[datum])
    }

    return config
  }, {})

  return camelCaseKeysInObject(nestedCamelCasedData)
}

const camelCaseKeysInArray = (arr) => {
  return arr.map(elem => camelCaseKeysInObject(elem))
}

const camelCaseKeysInObject = (obj) => {
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const camelCasedKey = camelCaseString(key)
      if (camelCasedKey !== key) {
        obj[camelCasedKey] = obj[key]
        delete obj[key]
      }

      if (typeof obj[camelCasedKey] === 'object') {
        if (Array.isArray(obj[camelCasedKey])) {
          obj[camelCasedKey] = camelCaseKeysInArray(obj[camelCasedKey])
        } else {
          obj[camelCasedKey] = camelCaseKeysInObject(obj[camelCasedKey])
        }
      }
    }
  }

  return obj
}
const toUpperCaseStringForCamel = (match, group) => {
  if (Number(group) >= 0 || Number(group) <= 9) {
    return `_${group}`
  }
  return group.toUpperCase()
}

const camelCaseString = (str) => str.replace(/_(.)/g, toUpperCaseStringForCamel)

export function snakeCaseKeys (data) {
  if (Array.isArray(data)) {
    throw Error('snakeCaseKeys doesn\'t support arrays for now')
  }

  return Object.keys(data).reduce((snakeCased, datum) => {
    const snakedCasedKey = datum.replace(/([A-Z])/g, ($1) => {
      return '_' + $1.toLowerCase()
    })
    snakeCased[snakedCasedKey] = data[datum]
    return snakeCased
  }, {})
}

export function getCookie (name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

