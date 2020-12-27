<template>
  <div>
    <MsgBox 
      v-bind:msgIn=msgIn 
      v-bind:callback="reset_msg" 
      v-bind:fw_func="fw_func" />
    <UserEdit 
      v-if="activeAct == 'edit' || activeAct == 'create'" 
      v-bind:act="activeAct" 
      v-bind:usr="activeEdit" 
      v-bind:reload="get_usr_data" 
      v-bind:callback="reset_act" />
    <UserPassword 
      v-if="activeAct == 'setpwd'" 
      v-bind:usr="activeEdit" 
      v-bind:callback="reset_act" />
    
    <table class="stdTable">
      <tr>
        <th v-for="(defi, idx) in defi" :key=idx :style="{ textAlign: defi.align }" >{{defi.hl}}</th>
        <th>Action</th>
      </tr>
      <tr v-for="(col, idx) in data" :key=idx>
        <td v-for="(defi, idx2) in defi" :key=idx2 :style="{ textAlign: defi.align }">{{col[defi.col]}}</td>
        <td>
          <ActionMenu 
            v-bind:uid=col.uid 
            v-bind:activeMenu=activeMenu 
            v-bind:set_active=set_active 
            v-bind:func_forward=func_forward />
        </td>
      </tr>
      <tr>
        <td :colspan=defi.length>
          <button v-on:click="guac_sync">sync with guacamole</button>  
        </td>
        <td>
          <button v-on:click="form_user_create">add</button>  
        </td>
      </tr>
    </table>
  </div>
</template>

<script>

import ActionMenu from './ActionMenu.vue'
import MsgBox from './MsgBox.vue'
import UserEdit from './UserEdit.vue'
import UserPassword from './UserPassword.vue'

export default {
  name: 'UserTable',
  components:{
    ActionMenu,
    MsgBox,
    UserEdit,
    UserPassword
  },
  props: {
    msg: String,
    callback: Function
  },
  data(){
    return{
      activeMenu: null,
      activeEdit: null, 
      activeAct: null,
      defi:[
        {
          "col": "uid",
          "hl": "UID",
          "align": "left"
        },
        {
          "col": "givenName",
          "hl": "Firstname",
          "align": "left"
        },
        {
          "col": "sn",
          "hl": "Lastname",
          "align": "left"
        },
        {
          "col": "homeDirectory",
          "hl": "Home Dir",
          "align": "left"
        },
        {
          "col": "loginShell",
          "hl": "Shell",
          "align": "left"
        }
      ],
      data: [],
      msgIn: "",
      fw_func: undefined,
      fwObj: {
        "edit": this.form_user_edit,
        "setpwd": this.form_user_setpwd,
        "member": this.form_user_member,
        "delete": this.fw_user_delete,
      },
    }
  },
  mounted(){
    this.get_usr_data();
    document.addEventListener('click', this.hide_menu);
  },
  beforeDestroy(){
    document.removeEventListener('click', this.hide_menu);
  },
  methods: {
    hide_menu(ev){
      var test = ev.target.getAttribute("tag");
      if(test != "menu"){
        this.activeMenu = null;
        //console.log(test);
      }
    },
    reset_msg(){
      this.msgIn = "";
      this.fw_func = undefined;
    },
    get_usr_data(){
      fetch('/api/users', {
        method: 'GET'
      })
      .then(response => response.json())
      .then(data => {
        console.log('Response:', data);
        if(data["data"]){
          this.data = data.data;
        }
        else{
          this.msgIn = "Something went wrong";
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        this.msgIn = "Something went wrong";
      });
    },
    set_active(uid){
      if(typeof uid == "string"){
        this.activeMenu = uid;
      }
    },
    reset_active(){
      this.activeMenu = null;
    },
    reset_act(){
      this.activeEdit = null;
      this.activeAct = null;
    },

    //---------------------------------------------
    func_forward(uid, act){
      this.reset_active();
      this.fwObj[act](uid);
    },
    
    form_user_create(){
      console.log("form create");
      this.activeEdit = "new";
      this.activeAct = "create";
    },
    form_user_edit(uid){
      console.log(uid, "form edit");
      this.activeEdit = uid;
      this.activeAct = "edit";
    },
    form_user_setpwd(uid){
      console.log(uid, "form setpwd");
      this.activeEdit = uid;
      this.activeAct = "setpwd";
    },
    form_user_member(uid){
      console.log(uid, "form member");
    },
    fw_user_delete(uid){
      this.msgIn = "Do you really want to delete this user "+uid+"?";
      this.fw_func = ()=>{ this.act_user_delete(uid) }
    },
    act_user_delete(uid){
      console.log(uid, "act delete");
      const data = {
        "uid": uid
      }
      fetch('/api/user/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(data),
      })
      .then(response => response.json())
      .then(data => {
        console.log('Response:', data);
        if(data.status == 200){
          this.get_usr_data();
        }
        else{
          this.msgIn = "Failed to detele user "+uid;
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        this.msgIn = "Failed to detele user "+uid;
      });
    },
    //---------------------------------------------
    
    guac_sync(){
      console.log("guac_sync");
      fetch('/api/users/sync', {
        method: 'POST',
      })
      .then(response => response.json())
      .then(data => {
        console.log('Response:', data);
        this.msgIn = "ldap users successfully synced with guacamole";
      })
      .catch((error) => {
        console.error('Error:', error);
        this.msgIn = "Failed to sync users with guacamole";
      });
    }

  }
}
</script>

<style scoped>
.stdTable{
  margin: 100px auto 40px auto;
  min-width: 800px;
}
.stdTable tr:last-child td{
  border: none;
  text-align: left;
}
.stdTable tr:last-child td:last-child{
  text-align: center;
}
.stdTable th{
  background-color: #2c3e50;
  color: #fff;
  font-size: 15px;
  font-weight: bold;
  padding:6px;
  border: 1px solid #000;
}
.stdTable td{
  background-color: #fff;
  color: #000;
  font-size: 15px;
  padding:6px;
  border: 1px solid #000;
}
.stdTable button{
  min-width: 50px;
  padding:2px 10px 2px 10px;
  margin: 8px auto auto auto;
  color: #fff;
  background-color: rgb(68, 23, 19);
  border: 2px solid rgb(36, 10, 7);
  border-radius: 6px;
  font-size: 13px;
  *font-weight: 600;
  cursor: pointer;
}
.stdTable button:hover{
  background-color: rgb(114, 38, 31);
}
</style>
