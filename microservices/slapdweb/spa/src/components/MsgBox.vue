<template >
  <div class="blocker" v-if="msgIn != ''" >
    <div class="msgBox" >
      <div css="hl" >System Message</div>
      <div css="msg">
        {{msgIn}}
      </div> 
      <div css="btnFrame" v-if="fw_func == undefined">
        <button v-on:click="callback" >ok</button>
      </div>
      <div css="btnFrame" v-if="fw_func != undefined">
        <button v-on:click="()=>{ this.fw_func(); this.callback(); }" >ok</button>
        <button v-on:click="callback" >cancel</button>
      </div>
    </div>
  </div>
</template>


<script>

export default {
  name: 'MsgBox',
  props: {
    msgIn: String,
    fw_func: Function,
    callback: Function
  },
  data(){
    return{
     
    }
  },
  mounted(){
  },
  methods: {
  }
}
</script>

<style scoped>

.msgBox{
  display: table;
  margin: 170px auto 40px auto;
  padding: 20px;
  min-width: 520px;
  min-height: 240px;
  border: 1px solid #444;
  border-radius: 10px;
  box-shadow: 2px 4px 10px #666;
  background-color:#fafafa;
}
.msgBox div[css=hl]{
  background-color: #2c3e50;
  color: #fff;
  font-size: 15px;
  font-weight: bold;
  text-align: center;
  padding:8px;
  margin-bottom: 14px;
  border: 1px solid #222;
  border-radius: 6px;
}
.msgBox div[css=msg]{
  padding: 14px;
  min-height: 100px;
  background-color: rgb(226, 232, 241);
  border: 1px solid #444;
  border-radius: 10px;
  text-align: center;
  font-size: 16px;
  color: #000;
}
.msgBox div[css=btnFrame]{
  padding:4px;
  text-align: center;
}
.msgBox div[css=btnFrame] button{
  min-width: 140px;
  padding:6px;
  margin: 18px 10px 2px 10px;
  color: #fff;
  background-color: rgb(68, 23, 19);
  border: 2px solid rgb(36, 10, 7);
  border-radius: 8px;
  font-size: 15px;
  *font-weight: 600;
  cursor: pointer;
}
.msgBox div[css=btnFrame] button:hover{
  background-color: rgb(114, 38, 31);
}
</style>
