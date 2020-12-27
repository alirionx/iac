<template>
  <div>
    <MsgBox v-bind:msgIn=msgIn v-bind:callback="reset_msg"/>
    <div class="loginForm" v-on:keyup.enter="auth_submit">
      <div css="hl">Admin Login</div>
      <input type="text" id="usrIpt" placeholder="User Name or Distinguished Name" v-model="usr" />
      <input type="password" id="pwdIpt" placeholder="Password" v-model="pwd" />
      <div css="btnFrame">
        <button v-on:click="auth_submit">submit</button>
      </div>
    </div>
  </div>
</template>

<script>
import MsgBox from './MsgBox.vue'

export default {
  name: 'LoginForm',
  components:{
    MsgBox
  },
  props: {
    msg: String,
    callback: Function
  },
  data(){
    return{
      usr: "",
      pwd: "",
      msgIn: '',
    }
  },
  methods: {
    auth_submit(){
      //-Input Check-----------------------
      var format = /[ `!@#$%^&*()_+\-\[\]{};':"\\|.<>\/?~]/;
      function high_light_elm(elm){
        var tmpCol = elm.style.borderColor;
        elm.style.borderColor = "red";
        setTimeout(function(){elm.style.borderColor = tmpCol}, 800);
      }

      var usrElm = document.getElementById("usrIpt");
      var pwdElm = document.getElementById("pwdIpt");
      //console.log(elm.value);
      if( format.test(usrElm.value) || usrElm.value == ""  ){
        high_light_elm(usrElm);
        return null;
      }
      if( pwdElm.value == ""  ){
        high_light_elm(pwdElm);
        return null;
      }
      //-----------------------------------

      const data = {
        "uid": this.usr,
        "pwd": this.pwd,
      }
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(data),
      })
      .then(response => response.json())
      .then(data => {
        console.log('Response:', data);
        if(data.status != 200){
          this.usr = "";
          this.pwd = "";
          //alert("Login Failed");
          this.msgIn = "Login Failed";
        }
        else{
          this.callback(this.usr);
        }
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    },
    reset_msg(){
      this.msgIn = '';
    }
  }
}
</script>

<style scoped>
.loginForm{
  display: table;
  margin: 170px auto 40px auto;
  padding: 20px;
  min-width: 500px;
  min-height: 200px;
  border: 1px solid #444;
  border-radius: 10px;
  box-shadow: 2px 4px 10px #666;
  background-color:#fafafa;
}
.loginForm div[css=hl]{
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
.loginForm input[type="text"], .loginForm input[type="password"] {
  width: 90%;
  padding: 10px;
  margin: 10px auto 10px auto;
  border: 0.5px solid #888;
  border-radius: 0px;
  text-align: center;
  font-size: 15px;
  box-shadow: 0 1px 1px #666;
}
.loginForm input[type="text"]:focus, .loginForm input[type="password"]:focus {
  background-color: rgb(242, 246, 255);
}
.loginForm div[css=btnFrame]{
  padding:4px;
  text-align: center;
}
.loginForm div[css=btnFrame] button{
  min-width: 140px;
  padding:6px;
  margin: 12px auto 2px auto;
  color: #fff;
  background-color: rgb(68, 23, 19);
  border: 2px solid rgb(36, 10, 7);
  border-radius: 8px;
  font-size: 15px;
  *font-weight: 600;
  cursor: pointer;
}
.loginForm div[css=btnFrame] button:hover{
  background-color: rgb(114, 38, 31);
}
</style>
