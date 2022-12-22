<template>
    <q-list separator>
        <q-item clickable v-ripple class="q-px-sm" v-for="(item, index) in numList.dataList" :key="index" @click="showDetail(item.id, item.times)">
            <q-item-section class="q-py-sm">
                <q-item-label class="text-subtitle1 text-weight-light text-grey-6 q-pl-md">第{{item.times}}回　{{item.lottery_date}}</q-item-label>
                <q-item-label style="white-space: nowrap;" class="text-h5 text-weight-light">
                    <span v-for="num_index in numCount" :key="num_index" class="q-pl-md ">{{item["number" + num_index]}}</span>
                    <span v-for="bonus_index in bonusCount" :key="bonus_index" 
                    class="text-body2 text-weight-light q-pl-sm" style="vertical-align:middle">({{item["bonus_" + bonus_index]}}) </span>
                </q-item-label>
            </q-item-section>
        </q-item>
    </q-list>
    <div v-intersection="onIntersection" class="text-center q-py-md">
        <q-spinner-pie :style="{visibility: toGetData ? 'visible': 'hidden'}" color="red-13" size="2em"/>
    </div>
    <q-dialog v-model="toShowDetail" full-height ref="detailPop" position="right" class="justify-start column">
        <q-card class="text-subtitle1 text-weight-light">
            <div class="q-px-lg q-py-sm bg-red-13 text-white">第{{detailData.time}}回　当選金額・口数</div>
            <q-list separator>
                <q-item v-for="index in winnerCount" :key="index" class="q-py-xs">
                    <q-item-section>
                        <div class="text-right row justify-between">
                                <div class="col-2 text-left">{{index}}等</div>
                                <div>
                                    <div class="col-6" v-if="detailData.data['amount_' + index]!=0">
                                        {{detailData.data["amount_" + index].toLocaleString()}} 円
                                    </div>
                                    <div class="col-4" v-if="detailData.data['amount_' + index]!=0">
                                        {{detailData.data["quantity_" + index].toLocaleString()}} 口
                                    </div>
                                    <div class="col-10" v-else>当該なし</div>
                                </div>
                        </div>
                    </q-item-section>
                </q-item>
                <q-item v-if="hasCarryOver" class="column">
                    <div>キャリーオーバー</div>
                    <div>{{detailData.data["carry_over"].toLocaleString()}} 円</div>
                </q-item>
                <q-item class="q-pa-lg flex justify-end">
                    <q-btn round label="" icon="close" color="grey-6" @click="detailPop.hide()"/>
                </q-item>
            </q-list>
        </q-card>
    </q-dialog>
</template>
<script setup>
import { ref, reactive, computed } from 'vue'
import { api } from 'src/boot/api'

const props = defineProps({
    numCount: Number,
    bonusCount: Number,
    winnerCount: Number,
    dataType: String})

const numCount = ref(props.numCount)
const bonusCount = ref(props.bonusCount)
const winnerCount = ref(props.winnerCount)
const toGetData = ref(true)
const toShowDetail = ref(false)
const detailPop = ref(null)
let numList = reactive({dataList: []})
let detailData = reactive({time: 0, data: {}})
let times = 0

function showDetail(id, time) {
    const path = "lottery_detail/" + props.dataType + "/" + id
    api.get(path).then(function (res) {
        if (res.data != null) {
            detailData.data = res.data
            detailData.time = time
            toShowDetail.value = true
        }
    })
}
const hasCarryOver = computed(() => {
  return 'carry_over' in detailData.data ? true : false
})

function onIntersection (entry) {
    toGetData.value = entry.isIntersecting
    setTimeout(() => {
        if (toGetData.value) {
            let path = "lottery_list/" + props.dataType
            if (times > 0) {
                path += '/' + times
            }
            api.get(path).then(function (res) {
                if (res.data != null && res.data.length > 0) {
                    numList.dataList = numList.dataList.concat(res.data)
                    times = res.data[res.data.length - 1].times - 1
                    toGetData.value = false
                }
            })
        }
    }, 200)
}
</script>

<style>

</style>