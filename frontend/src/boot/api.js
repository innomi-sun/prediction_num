import { ref } from 'vue'
import axios from 'axios'

let accessToken = ''
let userInfo = ref({ userName: '',
                roleCd: 0,
                email: '' })

const api = axios.create({ baseURL: process.env.resBaseUrl })
const apiAuth = axios.create({ baseURL: process.env.resBaseUrl})

function apiGetToken() {
  // Get access token by refresh token in auth domain cookie
  axios.get(process.env.authBaseUrl + 'token', {withCredentials: true})
    .then(function (res) {
      if (res.data != null && 'code' in res.data) {
        // When get new access token successed.
        if (res.data.code === 'I006' && 'access_token' in res.data && 'role_cd' in res.data) {
          userInfo.value = { userName: res.data.user_name,
                      roleCd: res.data.role_cd,
                      email: res.data.email }
          accessToken = res.data.access_token
          apiAuth.defaults.headers.common['Authorization'] = 'Bearer ' + accessToken
        }
      }
    })
    .catch(function (error) {
      accessToken = ''
    })
    .finally(function () {
      // always executed
    })

  // userInfo.value = { userName: "username",
  //   roleCd: 1,
  //   email: "email" }

  console.log("apiGetToken")
  
}

function apiToLoginPage() {
  window.open(process.env.loginUrl, '_blank').focus();
}

// Common logout function
function apiLogout() {
  
  // console.log("apiLogout")
  // userInfo.value = { userName: '', roleCd: 0, email: '' }
  // delete apiAuth.defaults.headers.common["Authorization"]
  // accessToken = ''

  axios.get(process.env.authBaseUrl + 'logout', {withCredentials: true})
  .then(function (res) {
    userInfo.value = { userName: '', roleCd: 0, email: '' }
    delete apiAuth.defaults.headers.common["Authorization"]
    accessToken = ''
  })
  .catch(function (error) {
    userInfo.value = { userName: '', roleCd: 0, email: '' }
    delete apiAuth.defaults.headers.common["Authorization"]
    accessToken = ''
  })
  .finally(function () {
    // always executed
  })

}

apiGetToken()
export { api, apiAuth, apiGetToken, apiLogout, apiToLoginPage, userInfo }