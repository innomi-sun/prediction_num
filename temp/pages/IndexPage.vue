<template>
  <q-page class="flex justify-center">
    <q-card class="full-width">
      <q-tabs
        v-model="tab"
        class="text-grey"
        active-color="red-13"
        indicator-color="red-13"
        align="justify"
      >
        <q-tab name="loto7" label="ロト７" class="q-py-sm"/>
        <q-tab name="loto6" label="ロト６"  class="q-py-sm"/>
        <q-tab name="miniloto" label="ミニロト"  class="q-py-sm"/>
        <q-tab name="num3" label="NUM３"  class="q-py-sm"/>
        <q-tab name="num4" label="NUM４"  class="q-py-sm"/>
      </q-tabs>
      <q-separator />

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="loto7" class="no-padding">
          <LotoNumList class="text-h6"></LotoNumList>
        </q-tab-panel>
        <q-tab-panel name="loto6">
          <div class="text-h6">ロト６</div>
          Lorem ipsum dolor sit amet consectetur adipisicing elit.
        </q-tab-panel>
        <q-tab-panel name="miniloto">
          <div class="text-h6">ミニロト</div>
          Lorem ipsum dolor sit amet consectetur adipisicing elit.
        </q-tab-panel>
        <q-tab-panel name="num3">
          <div class="text-h6">NUM３</div>
          Lorem ipsum dolor sit amet consectetur adipisicing elit.
        </q-tab-panel>
        <q-tab-panel name="num4">
          <div class="text-h6">NUM４</div>
          Lorem ipsum dolor sit amet consectetur adipisicing elit.
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import LotoNumList from 'components/LotoNumList.vue'
const tab = ref('loto7')
</script>
