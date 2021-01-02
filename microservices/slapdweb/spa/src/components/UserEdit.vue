<template>

  <div class="blocker" >
    <MsgBox v-bind:msgIn=msgIn v-bind:callback="reset_msg"/>
    <div class="actionForm" v-on:keyup.enter="edit_submit">
      <div css="hl">{{act}} user {{usr}}</div>
      
      <div v-for="(elm, idx) in defi" :key="idx">
        <div css="elmHl">{{elm.hl}}</div>
        <input v-if="elm.type=='text'" type="text" v-model="data[elm.col]" :placeholder="elm.placeholder" :id="'elm_'+elm.col" />
        <input v-if="elm.type=='static'" type="text" :disabled="true" v-model="data[elm.col]" :id="'elm_'+elm.col" />
        <select v-if="elm.type=='select'" type="dropdown" v-model="data[elm.col]" :id="'elm_'+elm.col" >
          <option v-for="(opt, idx2) in elm.options" :key="idx2" :value="opt.val">
            {{opt.txt}}
          </option>
        </select>
      </div>

      <div css="btnFrame">
        <button v-on:click="edit_submit">submit</button>
        <button v-on:click="callback">cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import MsgBox from './MsgBox.vue'

export default {
  name: 'UserEdit',
  components:{
    MsgBox
  },
  props: {
    act: String,
    usr: String,
    msg: String,
    callback: Function,
    reload: Function
  },
  data(){
    return{
      msgIn: '',
      defi:[
        {
          "col": "uid",
          "hl": "User ID",
          "type": "static",
          "placeholder": "no special characters",
          "regex": "^[A-Za-z0-9-]*$"
        },
        {
          "col": "cn",
          "hl": "Common Name",
          "type": "text",
          "placeholder": "no special characters",
          "regex": "^[A-Za-z0-9-]*$"
        },
        {
          "col": "givenName",
          "hl": "Firstname",
          "type": "text",
          "placeholder": "",
          "regex": "^.{2,}$"
        },
        {
          "col": "sn",
          "hl": "Lastname",
          "type": "text",
          "placeholder": "",
          "regex": "^.{2,}$"
        },
        {
          "col": "homeDirectory",
          "hl": "Home Directory",
          "type": "text",
          "placeholder": "local path",
          "regex": "^\\/(.)+$"
        },
        {
          "col": "loginShell",
          "hl": "Shell",
          "type": "text",
          "placeholder": "e.g /bin/bash",
          "regex": "^\\/(.)+$"
        },
        {
          "col": "employeeType",
          "hl": "Role",
          "type": "select",
          "placeholder": "",
          "regex": "^(.)+$",
          "options": [
            {
              "val": "user",
              "txt": "vdi user"
            },
            {
              "val": "admin",
              "txt": "vdi stack admin"
            }
          ]
        }        
      ],
      data: {
        "uid": "",
        "cn": "",
        "givenName": "",
        "sn": "",
        "homeDirectory": "",
        "loginShell": "",
        "employeeType": "user",
      }
    }
  },
  mounted(){
    if(this.act == "edit"){
      this.call_userdata();
    }
    if(this.act == "create"){
      this.data["uid"] = this.usr;
    }
  },
  methods: {
    reset_msg(){
      this.msgIn = '';
    },
    call_userdata(){
      fetch('/api/user/'+this.usr, {
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
    edit_submit(){
      //console.log(this.data);
      var chk = true;
      const data = {}
      for(var idx in this.defi){
        var defi = this.defi[idx];
        var re = new RegExp(defi.regex);
        var reRes = re.test(this.data[defi.col]);
        //console.log(reRes, defi.col, defi.regex );
        
        if(! reRes){
          this.data[defi.col] = '';
          this.highlight_border_color("elm_"+defi.col);
          chk = false;
        }
        else{
          data[defi.col] = this.data[defi.col];
        }
      
      }
      if(chk){
        fetch('/api/user/'+this.act, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json'},
          body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
          console.log('Response:', data);
          if(data.status != 200){
            this.msgIn = "Something went wrong";
          }
          else{
            this.reload();
            this.callback();
          }
        })
        .catch((error) => {
          console.error('Error:', error);
          this.msgIn = "Something went wrong";
        });
      }
        
    },
    highlight_border_color(domid){
      var elm = document.getElementById(domid);
      var tmpCol = elm.style.borderColor;
      elm.style.borderColor = 'red';
      setTimeout( function(){ elm.style.borderColor = tmpCol}, 800 );
    }
  }
}
</script>

<style scoped>

</style>
