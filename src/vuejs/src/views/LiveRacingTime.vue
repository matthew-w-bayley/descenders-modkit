<template>
    <v-container fluid class="fill-height">
      <v-row align="center" justify="center">
        <v-col cols="auto">
          <h1 class="text-h3 tag-format">{{secs_to_str(user_time)}}</h1>
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
        users: [],
        user_time: "",
      }
    },
    computed: {
      ourSteamId() {
        return this.$route.query.steam_id;
      },
      get_latest_trail(){
        // so user['trails'] is list of trails with time_started, times, and started
        // we want to get the latest trail
        if (this.spectatedPlayer === "Loading..." || this.spectatedPlayer === undefined){
          return undefined;
        }
        console.log(this.spectatedPlayer)
        // [{'trail_name': 'Igloo BMX Track', 'started': True, 'time_started': 1740705443.1340623, 'times': []}]
        var trails = this.spectatedPlayer.trails; // this is a list of {trail_name: 'name', time_started: 123, times: [1, 2, 3], started: true}
        const formattedString = trails
          .replace(/'/g, '"')  // Replace all single quoteswith double quotes
          .replace(/\bFalse\b/g, 'false') // Replace Python-style `False` with JavaScript `false`
          .replace(/\bTrue\b/g, 'true'); // Replace Python-style `True` with JavaScript `true`
        trails = JSON.parse(formattedString);

        // sort the trails by time_started
        trails.sort((a, b) => {
          return a.time_started - b.time_started;
        });
        // get the last trail
        return trails[trails.length - 1];
      },
      ourPlayer(){
        return this.users.find(u => u.steam_id === this.ourSteamId);
      },
      spectatedPlayer(){
        var ourPlayer = this.ourPlayer;
        if (ourPlayer === undefined){
          return "Loading...";
        }
        return this.users.find(u => u.steam_id === ourPlayer.spectating_id);
      }
    },
    methods : {
      secs_to_str(secs){
            secs = parseFloat(secs);
            var d_mins = Math.floor(secs / 60);
            var d_secs = Math.floor(secs % 60)
            var fraction = secs * 1000;
            fraction = Math.round(fraction % 1000);
            d_mins = d_mins.toString();
            d_secs = d_secs.toString();
            fraction = fraction.toString();
            if (d_mins.length == 1)
                d_mins = "0" + d_mins.toString()
            if (d_secs.length == 1)
                d_secs = "0" + d_secs
            while (fraction.length < 3)
                fraction = "0" + fraction
            return d_mins + ":" + d_secs + "." + fraction
        },
    },
    mounted() {
      setInterval(() => {
        // get the latest trail
        var latest_trail = this.get_latest_trail;
        if (latest_trail === undefined){
          this.user_time =  "Loading...";
        }
        // if the trail is not started but times is not empty
        if (latest_trail.started === false && latest_trail.times.length > 0){
          // get the last time
          this.user_time =  latest_trail.times[latest_trail.times.length - 1];
        }
        // if the trail is started
        if (latest_trail.started === true){
          // get the time since the trail started
          this.user_time = (Date.now()/1000) - latest_trail.time_started;
        }
      }, 1);

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