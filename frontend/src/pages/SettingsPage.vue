<template>

    <q-list bordered class="rounded-borders">
      <q-item v-if="userInfo.roleCd > 0" clickable v-ripple class="q-pa-lg">
        <q-item-section avatar>
            <q-icon name="person" />
        </q-item-section>
        <q-item-section>{{userInfo.email}}</q-item-section>
      </q-item>
      <q-separator />
      <q-expansion-item icon="fact_check" label="利用規約" class="q-pa-sm">
        <q-card>
          <q-card-section><div v-html="htmlRule"></div></q-card-section>
        </q-card>
      </q-expansion-item>
      <q-separator />
      <q-expansion-item icon="policy" label="プライバシーポリシー" class="q-pa-sm">
        <q-card>
          <q-card-section><div v-html="htmlPrivacy"></div></q-card-section>
        </q-card>
      </q-expansion-item>
      <q-separator />
      <q-item v-if="userInfo.roleCd > 0" clickable v-ripple class="q-pa-lg" @click="(confirmDlg=!confirmDlg)">
        <q-item-section avatar>
            <q-icon name="logout" />
        </q-item-section>
        <q-item-section>ログアウト</q-item-section>
      </q-item>
    </q-list>
    <q-dialog v-model="confirmDlg">
      <q-card class="q-pa-sm" >
        <q-card-section class="q-pa-lg text-body1 text-weight-light">
          <span>ログアウトしてよろしいでしょうか</span>
        </q-card-section>
        <q-card-actions align="right" >
            <q-btn flat label="はい" class="text-body1 text-weight-light" color="red-13" @click="apiLogout()" v-close-popup />
            <q-btn flat label="キャンセル" color="grey-6" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { apiLogout, userInfo } from 'src/boot/api'

let htmlRule = ref("")
let htmlPrivacy = ref("")
const confirmDlg = ref(false)

axios.get("./rule.html").then(function (res) {
    if (res.data != null) {
      htmlRule.value = res.data
    }
})
axios.get("./privacy.html").then(function (res) {
    if (res.data != null) {
      htmlPrivacy.value = res.data
    }
})

</script>
