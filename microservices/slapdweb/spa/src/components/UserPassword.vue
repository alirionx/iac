<template>

  <div class="blocker" >
    <MsgBox v-bind:msgIn=msgIn v-bind:callback="reset_msg"/>
    <div class="actionForm" v-on:keyup.enter="pwdset_submit">
      <div css="hl">Set Password for user {{usr}}</div>
      
      <input type="password" id="pwdIn" :placeholder="'Enter new password (min '+pwdLength+' characters)'" v-model="pwdIn" />
      <input type="password" id="pwdRep" :placeholder="'Repeat new password'" v-model="pwdRep" />

      <div css="btnFrame">
        <button v-on:click="pwdset_submit">submit</button>
        <button v-on:click="callback">cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import MsgBox from './MsgBox.vue'

export default {
  name: 'UserPassword',
  components:{
    MsgBox
  },
  props: {
    usr: String,
    msg: String,
    callback: Function
  },
  data(){
    return{
      msgIn: '',
      pwdIn: '',
      pwdRep: "",
      pwdLength: 4

    }
  },
  mounted(){
 
  },
  methods: {
    reset_msg(){
      this.msgIn = '';
    },
    pwdset_submit(){

      if(this.pwdIn.length < this.pwdLength){
        this.highlight_border_color("pwdIn");
        this.pwdIn = "";
        this.pwdRep = "";
        this.msgIn = "Password to short";
        return;
      }
      if(this.pwdIn != this.pwdRep){
        this.highlight_border_color("pwdRep");
        this.pwdRep = "";
        this.msgIn = "Password repeat does not fit.";
        return;
      }

      const data = {
        "uid": this.usr,
        "pwd": this.pwdIn
      }
      fetch('/api/user/setpwd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(data),
      })
      .then(response => response.json())
      .then(data => {
        console.log('Response:', data);
        if(data.status == 200){
          this.msgIn = "OK";
          this.callback();
        }
        else{
          this.msgIn = "Something went wrong.";
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        this.msgIn = "Something went wrong.";
      });

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
  .actionForm input[type="password"]{
  width: 80%;
  padding: 8px;
  margin: 4px auto 10px auto;
  border: 0.5px solid #888;
  border-radius: 0px;
  text-align: center;
  font-size: 15px;
  box-shadow: 0 1px 1px #666;
}
.actionForm input[type="password"]:focus {
  background-color: rgb(242, 246, 255);
}

</style>
