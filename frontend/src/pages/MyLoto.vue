<template>
    <q-page class="flex justify-start column">
        <span v-if="toGetData" class="text-center q-py-md">
            <q-spinner-pie color="red-13" size="2em"/>
        </span>
        <div v-if="userInfo.roleCd > 0 && myNumList.length == 0" class="text-subtitle1 text-grey-6 text-center q-py-xl">「+」ボタンで気になる数字を追加してください。</div>
        <q-list separator>
            <q-item clickable v-ripple class="q-px-sm" v-for="(item, index) in myNumList" :key="index" @click="showDetail(item.id)">
                <q-item-section class="q-py-sm">
                    <q-item-label class="text-subtitle1 text-weight-light text-grey-6 q-pl-md">{{selectOpt[item.lottery_type].label}}　{{item.comment}}</q-item-label>
                    <q-item-label class="text-h5 text-weight-light q-pl-md">
                        <span v-for="num in item.my_numbers" :key="num" class="q-pr-md">{{num}}</span>
                    </q-item-label>
                </q-item-section>
            </q-item>
        </q-list>
        <q-separator v-if="myNumList.length > 0"/>
        <div v-if="userInfo.roleCd == 0" class="text-subtitle1 text-grey-6 q-pa-xl column">
            <q-btn rounded label="ログインしてマイロトを追加" color="red-13" class="q-mx-lg no-wrap" @click="apiToLoginPage()"/>
        </div>
    </q-page>
    <q-page-sticky v-if="userInfo.roleCd > 0 && myNumList.length < $maxMylotoCountLevel1" position="bottom-right" :offset="[8, 75]">
        <q-btn round glossy color="primary" icon="add" size="md" @click="showDetail()"/>
    </q-page-sticky>
    <q-dialog v-model="isDetail" full-height ref="detailPop" position="right" class="text-weight-light">
        <q-card class="column no-wrap">
            <div class="q-pa-sm bg-red-13 text-h6 text-white text-weight-light text-center">{{detailTitle}}</div>
            <div class="q-px-lg">
                <q-select outlined dense v-model="lotoType" :options="selectOpt" @update:model-value="updateLoto" 
                    label="ロト種別" label-color="red-13" color="red-13" class="q-ma-sm q-px-xl"/>
            </div>
            <div class="row q-px-md q-mx-auto" style="width:320px">
                <div class="q-pr-xs q-pb-xs col-2" v-for="(number, num_index) in $lotoAllNum[lotoType.value]" :key="num_index">
                    <q-btn class="text-body1 text-weight-light" :outline="!numSelected.includes(number)" round dense color="red-13" @click="setNum(number)" :label="number"/>
                </div>
            </div>
            <div class="q-pa-md">
                <q-input v-model="numComment" maxlength="50" label-color="red-13" filled label="コメント入力"/>
            </div>
            <div class="q-px-md q-gutter-sm row justify-end">
                    <q-btn rounded label="保存" icon="done" color="red-13" @click="saveNum()"/>
                    <q-btn v-if="numSelectedId" rounded label="削除" icon="delete" color="grey-6" @click="confirmDlg=true"/>
                    <q-btn round label="" icon="close" color="grey-6" @click="closeNumDetail()"/>
            </div>           
        </q-card>
    </q-dialog>
    <q-dialog v-model="confirmDlg">
      <q-card class="q-pa-sm" >
        <q-card-section class="q-pa-lg text-body1 text-weight-light">
          <span>削除してよろしいでしょうか</span>
        </q-card-section>
        <q-card-actions align="right" >
            <q-btn flat label="はい" class="text-body1 text-weight-light" color="red-13" @click="deleteNum" v-close-popup />
            <q-btn flat label="キャンセル" color="grey-6" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
</template>
<script setup>
import { ref, onMounted, watch, getCurrentInstance } from 'vue'
import { apiAuth, apiToLoginPage, userInfo } from 'src/boot/api'

const $gp = getCurrentInstance().appContext.config.globalProperties
const toGetData = ref(false)
const isDetail = ref(false)
const detailTitle = ref("")
const confirmDlg = ref(false)
const detailPop = ref(null)
let lotoType = ref({ label: 'ロト７', value: 'loto7' })
let numComment = ref(null)
let myNumList = ref([])
let numSelected = ref([])
let numSelectedId = ref(null)
const selectOpt = [ 
    { label: 'ロト７', value: 'loto7' }, 
    { label: 'ロト６', value: 'loto6' }, 
    { label: 'ミニロト', value: 'miniloto' }, 
    { label: 'NUM４', value: 'numbers4' }, 
    { label: 'NUM３', value: 'numbers3' } ]

function showDetail(id) {
    if (id == null) {
        detailTitle.value = "マイロト追加"
        lotoType.value = { label: 'ロト７', value: 'loto7' }
        numSelected.value = []
        numSelectedId.value = null
        numComment.value = ""
    } else {
        myNumList.value.forEach((num) => {
            const item = JSON.parse(JSON.stringify(num))
            if (item.id == id) {
                detailTitle.value = "マイロト編集"
                lotoType.value = selectOpt[item.lottery_type]
                numSelectedId.value = id
                numSelected.value = item.my_numbers
                numComment.value = item.comment
                return
            }
        })
    }
    isDetail.value = true
}
function getMyNumList() {
    toGetData.value = true
    apiAuth.get("my_numbers_list").then(function (res) {
        if (res.data != null) {
            myNumList.value = res.data
            toGetData.value = false
        }
    })
}
function setNum(num) {
    const index = numSelected.value.indexOf(num)
    if (index == -1) {
        if (numSelected.value.length < $gp.$lotoNumCount[lotoType.value.value]) {
            numSelected.value.push(num)
        }
    } else {
        numSelected.value.splice(index, 1)
    }
    numSelected.value.sort((a, b) => {return a - b})
}
function updateLoto() {
    numSelected.value = []
}
function saveNum() {
    const path = process.env.resBaseUrl + 'my_numbers'
    apiAuth.post(path, {
        "my_numbers_id": numSelectedId.value,
        "lottery_type": $gp.$lotoNumTypeId[lotoType.value.value],
        "numbers": numSelected.value,
        "comment": numComment.value
    }).then(function (res) {
        detailPop.value.hide()
        numSelected.value = []
        numComment.value = ""
        getMyNumList()
    })
}
function closeNumDetail() {
    detailPop.value.hide()
}
function deleteNum() {
    if (numSelectedId.value != null) {
        apiAuth.delete('my_numbers', {
            data: {"my_numbers_id": numSelectedId.value}
        }).then(function (res) {
            getMyNumList()
            numSelectedId.value = null
            confirmDlg.value = false
            isDetail.value = false
        })
    }
}

onMounted(() => {
  if (userInfo.value.roleCd > 0)
    getMyNumList()
})

watch(() => userInfo.value.roleCd, (roleCd) => {
  if (roleCd > 0)
    getMyNumList()
})

</script>

<style>

</style>