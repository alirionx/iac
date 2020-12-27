<template >
  <div tag="menu" class="menuFrame">
    <div tag="menu" class="actMenuBtn" v-on:click="set_active(uid)" >
      <div tag="menu" css="dot"></div>
      <div tag="menu" css="dot"></div>
      <div tag="menu" css="dot"></div>
    </div>

    <div class="actMenuFrame" v-if="activeMenu == uid" >
      <div css="arrow"></div>
      <div css="btn" v-for="(act, idx) in menuActs" :key=idx v-on:click="func_forward(uid, act.act)" >{{act.txt}}</div>
    </div>
  </div>
</template>


<script>

export default {
  name: 'ActionMenu',
  props: {
    activeMenu: String,
    uid: String,
    set_active: Function,
    func_forward: Function
  },
  data(){
    return{
      menuActs:[
        {
          txt: "Edit",
          act: "edit"
        },
        {
          txt: "Set Password",
          act: "setpwd"
        },
        {
          txt: "Delete",
          act: "delete"
        },
        {
          txt: "Memberships",
          act: "member"
        }
      ],
    }
  },
  mounted(){
    
  },
  methods: {
    
  }
}
</script>

<style scoped>
.menuFrame{
  display: inline-block;
  position: relative;
}
.actMenuBtn{
  display: inline-block;
  margin: -7px auto -7px auto;
  padding:1px;
  border: 1px solid rgb(68, 23, 19);
  border-radius: 3px;
  cursor: pointer;
}
.actMenuBtn div[css=dot]{
  width:12px;
  height: 4px;
  border-radius: 4px;
  margin: 2px;
  background: rgb(68, 23, 19);
}
.actMenuBtn:hover{
  background-color: rgb(68, 23, 19);
}
.actMenuBtn:hover div[css=dot]{
  background: rgb(255, 243, 243);
}

.actMenuFrame{
  position: absolute;
  left: 40px;
  top:-3px;
  min-width: 100px;
  *border:1px solid rgb(39, 10, 8);
  z-index: 3;
}
.actMenuFrame div[css=arrow]{
  position: absolute;
  left:-19px;
  top:4px;
  width: 0; 
  height: 0; 
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent; 
  border-right:18px solid rgb(73, 27, 22);
}
.actMenuFrame div[css=btn]{
  background-color: rgb(73, 27, 22);
  border:1px solid #000;
  margin-bottom: -1px;
  color: #fff;
  text-align: center;
  font-size: 13px;
  padding: 4px;
  border-radius: 2px;
  cursor: pointer;
}
.actMenuFrame div[css=btn]:hover{
  background-color: rgb(114, 38, 31);
}

</style>
