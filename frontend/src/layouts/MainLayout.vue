<template>
  <q-layout view="lHh Lpr lFf">
    <q-header reveal elevated class="bg-red-13 text-white text-center">
      <q-toolbar>
        <q-toolbar-title class="text-h6">
          {{title}}
        </q-toolbar-title>
      </q-toolbar>
    </q-header>
    <q-page-container>
      <router-view />
    </q-page-container>
    <q-page-sticky position="bottom-right" :offset="[50, 30]">
      <q-btn color="red-13" round glossy icon="menu" size="lg">
        <q-menu class="bg-red-13 text-white" :offset="[0, 8]" auto-close transition-show="jump-up" transition-hide="jump-down">
          <q-list separator bordered style="min-width: 180px">
            <q-item clickable @click="menuClick('/')">
              <q-item-section avatar><q-icon name="fact_check" /></q-item-section>
              <q-item-section>抽選結果</q-item-section>
            </q-item>
            <q-item clickable @click="menuClick('/aiPred')">
              <q-item-section avatar><q-icon name="lightbulb" /></q-item-section>
              <q-item-section>aiちゃん予測</q-item-section>
            </q-item>
            <q-item clickable @click="menuClick('/myLoto')">
              <q-item-section avatar><q-icon name="filter_7" /></q-item-section>
              <q-item-section>マイロト</q-item-section>
            </q-item>
            <q-item clickable @click="menuClick('/settings')">
              <q-item-section avatar><q-icon name="settings" /></q-item-section>
              <q-item-section>設置</q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>

    </q-page-sticky>
    <q-page-scroller position="bottom-right" :scroll-offset="500" :offset="[8, 15]">
        <q-btn round glossy color="grey-6" icon="keyboard_arrow_up" size="md"/>
    </q-page-scroller>    
  </q-layout>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { apiGetToken, userInfo } from 'src/boot/api'

const $q = useQuasar()
console.log(userInfo)
watch(() => $q.appVisible, (val) => {
  if (val && userInfo.value.roleCd <= 0)
    apiGetToken()
})

const router = useRouter()
const menuTitle = {'/': '抽選結果', '/aiPred': 'aiちゃん予測', '/myLoto': 'マイロト', '/settings': '設置'}
let title = ref(menuTitle[router.currentRoute.value.path])
function menuClick(to) {
  title.value = menuTitle[to]
  router.push(to)
}
</script>
<style>
.main-menu {
  font-size: 16px;
  width: 150px;
}
</style>