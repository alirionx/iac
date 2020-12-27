<template>
  <div id="app" >
    <MsgBox v-bind:msgIn=msgIn v-bind:callback="reset_msg"/>
    <div class="headBlock">
      <div css="hl">VDI Stack - User Management WebUi</div>
      <div css="logoutBtn" v-if="usr !== false" v-on:click="logout">logout</div>
    </div>
    <LoginForm v-if="usr == false" v-bind:callback="set_usr" />
    <UserTable v-if="usr != false" />
    
  </div>
</template>

<script>
import MsgBox from './components/MsgBox.vue'
import LoginForm from './components/LoginForm.vue'
import UserTable from './components/UserTable.vue'

export default {
  name: 'App',
  components: {
    LoginForm,
    UserTable,
    MsgBox
  },
  data(){
    return{
      usr: false,
      msgIn: '',
    }
  },
  mounted(){
    this.chk_auth_state();
  },
  methods: {
    chk_auth_state(){
      fetch('/api/auth/check', {
        method: 'GET'
      })
      .then(response => response.json())
      .then(data => {
        console.log('Response:', data);
        if(data.status == 200 && data.uid != undefined){
          this.usr = data.uid;
        }
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    },
    set_usr(usr){
      this.usr = usr;
    },
    logout(){
      const data = {
        "uid": this.usr
      }
      fetch('/api/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(data),
      })
      .then(response => response.json())
      .then(data => {
        if(data.status == 200 ){
          this.usr = false;
        }
        else{
          //this.msgIn = "Logout Failed";
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        this.msgIn = "Something went wrong";
      });
    },
    reset_msg(){
      this.msgIn = '';
    }

  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  *color: #2c3e50;
  margin-top: 120px;
}
.headBlock{
  position: fixed;
  left: 0px;
  top: 0px;
  width: 100%;
  height: 80px;
  background-color: #2c3e50;
  text-align: center;
  color: #fff;
  z-index: 10;
}
.headBlock div[css=hl]{
  font-size: 20px;
  padding: 30px;
  font-weight: 500;
  display:inline-block;
  *background-color: #35485c;
}
.headBlock div[css=logoutBtn]{
  font-size: 12px;
  position: absolute;
  right:14px;
  bottom:10px;
  font-weight: 600;
  cursor: pointer;
}
.headBlock div[css=logoutBtn]:hover{
  text-decoration: underline;
}

.blocker{
  position:fixed;
  left: 0;
  top: 0;
  width: 100%;
  height: 100vh;
  background-color: rgba(255,255,255,0.6);
  z-index: 2;
}
::placeholder {
  color: rgb(211, 184, 184)
}
.actionForm{
  display: table;
  margin: 100px auto 40px auto;
  padding: 20px;
  min-width: 600px;
  min-height: 200px;
  border: 1px solid #444;
  border-radius: 10px;
  box-shadow: 2px 4px 10px #666;
  background-color:#fafafa;
}
.actionForm div[css=hl]{
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
.actionForm div[css=elmHl]{
  width: 92%;
  display: inline-block;
  color: #000;
  font-size: 13px;
  font-weight: bold;
  text-align: left;
  text-decoration: underline;
  padding:8px 0 1px 0;
}

.actionForm input[type="text"]{
  width: 90%;
  padding: 8px;
  margin: 4px auto 10px auto;
  border: 0.5px solid #888;
  border-radius: 0px;
  text-align: left;
  font-size: 15px;
  box-shadow: 0 1px 1px #666;
}
.actionForm input[type="text"]:focus {
  background-color: rgb(242, 246, 255);
}
.actionForm input[disabled]{
  background-color: #eee;
}

.actionForm div[css=btnFrame]{
  padding:4px;
  text-align: center;
}
.actionForm div[css=btnFrame] button{
  min-width: 140px;
  padding:6px;
  margin: 16px 10px 2px 10px;
  color: #fff;
  background-color: rgb(68, 23, 19);
  border: 2px solid rgb(36, 10, 7);
  border-radius: 8px;
  font-size: 15px;
  *font-weight: 600;
  cursor: pointer;
}
.actionForm div[css=btnFrame] button:hover{
  background-color: rgb(114, 38, 31);
}

</style>
 