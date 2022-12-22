<template>
  <q-page class="flex justify-start column">
    <div v-if="userInfo.roleCd == 0" class="text-subtitle1 q-pa-xl column">
      <q-btn rounded label="ログインして予測数字をゲット" color="red-13" class="q-mx-lg no-wrap" @click="apiToLoginPage()"/>
    </div>
    <span v-if="(toGetData && userInfo.roleCd > 0)" class="text-center q-py-md">
      <q-spinner-pie color="red-13" size="2em"/>
    </span>
    <q-card class="q-mx-sm q-my-xs q-px-md q-py-sm" v-if="(aiNumList.length > 0)">
      <div class="column">
        <q-chip size="sm">
          <q-avatar dense text-color="white" color="red-13">AI</q-avatar>
          <span class="text-caption"> AIモジュールで次回当選数字を予測</span>
        </q-chip>
        <q-chip size="sm">
          <q-avatar dense text-color="white" color="primary" class="pred-chip">数</q-avatar>
          <span class="text-caption"> 数理分析で次回当選数字を予測</span>
        </q-chip>
      </div>
    </q-card>
    <q-card v-for="(item, index) in aiNumList" :key="index" class="q-mx-sm q-my-xs q-pa-sm">
      <span class="text-subtitle1 text-grey-6">{{lotoTypeTitle[item.lottery_type]}} {{item.itemName}} 第{{item.next_times}}回  {{item.next_date}}</span>
      <q-card-section class="q-pa-xs justify-start row text-h5">
        <div class="q-pa-sm row col-2 no-wrap text-weight-light" v-for="(number, num_index) in $lotoAllNum[item.lottery_type]" :key="num_index">
          <div>{{number}}</div>
          <div class="column">
            <q-chip v-if="item.predict_num.includes(number)" dense text-color="white" color="red-13" class="pred-chip">AI</q-chip>
            <q-chip v-if="staNumList[index].predict_num.includes(number)" dense text-color="white" color="primary" class="pred-chip">数</q-chip>
          </div>
        </div>					
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { apiAuth, apiToLoginPage, userInfo } from 'src/boot/api'

let aiNumList = ref([])
let staNumList = ref([])
let lotoTypeTitle = ref({loto7: "ロト７", loto6: "ロト６", miniloto: "ミニロト", numbers4: "NUM４", numbers3: "NUM３"})
const toGetData = ref(false)

function getData () {
  toGetData.value = true
  Promise.all([
    apiAuth.get("ai_numbers"), 
    apiAuth.get("sta_numbers")
 ])
 .then((res) => {
    if (res[0].data && res[0].data.length > 0) {
        aiNumList.value = res[0].data
    }
    if (res[1].data && res[1].data.length > 0) {
        staNumList.value = res[1].data
    }    
    toGetData.value = false
 })
}

onMounted(() => {
  if (userInfo.value.roleCd > 0)
    getData()
})

watch(() => userInfo.value.roleCd, (roleCd) => {
  if (roleCd > 0)
    getData()
})

</script>
<style>
.pred-chip {
  font-size: 10px;
  margin: 1px 1px 1px 0px;
}
</style>