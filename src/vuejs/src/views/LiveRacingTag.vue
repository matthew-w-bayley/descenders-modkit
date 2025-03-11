<template>
    <v-container fluid class="fill-height">
      <v-row align="left" justify="left">
        <v-col cols="auto">
          <h1 class="text-h3 tag-format">{{spectatedPlayer}}</h1>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <style>
    .tag-format{
      font-size: 20px;
      font-weight: bold;
    }
  </style>

  <script>
    export default {
    name: 'App',
    data() {
      return {
        users: []
      }
    },
    computed: {
      ourSteamId() {
        return this.$route.query.steam_id;
      },
      ourPlayer(){
        return this.users.find(u => u.steam_id === this.ourSteamId);
      },
      spectatedPlayer(){
        var ourPlayer = this.ourPlayer;
        if (ourPlayer === undefined){
          return "Loading...";
        }
        return ourPlayer.spectating;
      }
    },
    mounted() {

        // the steam_id should be given to us in the url
        this.ourSteamId = this.$route.params.steam_id;

        this.$socket.on('users_update', (data) => {
        // data is like [{steam_id: 123, steam_name: 'name', eval: 'eval'}, ...]
        data.forEach(user => {
          // if user exists, update it, otherwise add it
          let index = this.users.findIndex(u => u.steam_id === user.steam_id);
          if (index !== -1) {
            // UPDATE (do not remove existing keys)
            for (const [key, value] of Object.entries(user)) {
              this.users[index][key] = value;
            }
          } else {
            // ADD
            this.users.push(user);            
          }
        });
        // remove users that are not in the data
        this.users = this.users.filter(u => data.find(d => d.steam_id === u.steam_id));
      })
      this.$socket.emit('message', 'get_users');
      setInterval(() => {
        this.$socket.emit('message', 'get_users');
      }, 800);
    }
  }
  </script>