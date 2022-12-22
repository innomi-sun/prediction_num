
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/LotoResult.vue') },
      { path: 'aiPred', component: () => import('pages/AiPrediction.vue') },
      { path: 'myLoto', component: () => import('pages/MyLoto.vue') },
      { path: 'settings', component: () => import('pages/SettingsPage.vue') }
      // {
      //   path: "threeJSTest",
      //   component: () => import("pages/ThreeJSTest.vue"),
      // }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
