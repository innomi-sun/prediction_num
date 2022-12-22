<template>
  <q-page >
    <q-card class="window-height" v-touch-swipe.mouse.left="handleSwipe" v-touch-swipe.mouse.right="handleSwipe">
      <q-tabs
        v-model="tab"
        class="text-grey"
        active-color="red-13"
        indicator-color="red-13"
        align="justify"
      >
        <q-tab v-for="item in lotos" :key="item.type" :name="item.type" :label="item.title" class="q-py-sm"/>
      </q-tabs>
      <q-separator />
      <q-tab-panels v-model="tab" animated >
        <q-tab-panel v-for="item in lotos" :key="item.type" :name="item.type" class="no-padding">
          <LotoNumList :numCount="item.numCount" :bonusCount="item.bonusCount" :winnerCount="item.winnerCount" :dataType="item.type"/>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import LotoNumList from 'components/LotoNumList.vue'
const tab = ref('loto7')
const lotos = [
  {type: "loto7", title: "ロト７", numCount: 7, bonusCount: 2, winnerCount: 6},
  {type: "loto6", title: "ロト６", numCount: 6, bonusCount: 1, winnerCount: 5},
  {type: "miniloto", title: "ミニロト", numCount: 5, bonusCount: 1, winnerCount: 4},
  {type: "numbers4", title: "NUM４", numCount: 4, bonusCount: 0, winnerCount: 4},
  {type: "numbers3", title: "NUM３", numCount: 3, bonusCount: 0, winnerCount: 5}
]

function handleSwipe ({ evt, ...swipeInfo }) {
  if (swipeInfo.distance.x > 8 && swipeInfo.duration > 10) {
    let next = 0
    for (let i = 0; i < lotos.length; i++) {
      if (lotos[i].type == tab.value) {
        if (swipeInfo.direction == "left") {
          next = i + 1
        } else if (swipeInfo.direction == "right") {
          next = i - 1 < 0 ? lotos.length - 1 : i - 1
        }
        console.log(lotos[Math.abs(next) % lotos.length].type)
        tab.value = lotos[Math.abs(next) % lotos.length].type
        break
      }
    }
  }
}

</script>
