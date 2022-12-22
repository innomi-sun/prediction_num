<template>
  <q-layout view="lHh Lpr lFf">
    <q-header reveal elevated class="bg-red-13 text-white text-center">
      <q-toolbar>
        <q-toolbar-title>
          抽選結果
        </q-toolbar-title>
      </q-toolbar>
    </q-header>
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import EssentialLink from 'components/EssentialLink.vue'

const linksList = [
  {
    title: 'threeJSTest',
    caption: 'quasar.dev',
    icon: 'school',
    link: "/threeJSTest",
  }
]


</script>
