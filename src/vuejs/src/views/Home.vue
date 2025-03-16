<template>
    <v-container class="fill-height d-flex justify-center">
      <v-responsive
        class="align-center fill-height mx-auto"
        :max-width="height"
      >
        <v-img
          class="mb-4"
          height="150"
          src="@/assets/logo.png"
        />

        <div class="text-center">
          <div class="text-body-2 font-weight-light mb-n1">Welcome to the</div>
          <h1 class="text-h2 font-weight-bold">Descenders Modkit</h1>
          <div class="text-body-2 font-weight-light mb-n1">Developed on behalf of Descenders Competitive.</div>
        </div>

        <div class="py-4" />
    
        <v-row align="center" justify="center">
          <v-col cols="12" md="6" sm="12" xs="12">
            <v-card
              append-icon="mdi-open-in-app"
              class="py-4"
              color="surface-variant"
              prepend-icon="mdi-text-box-outline"
              :to="'/leaderboard'"
              rel="noopener noreferrer"
              rounded="lg"
              subtitle="See all of the trails and find the fastest times."
              title="Leaderboard"
              variant="text"
            >
              <v-overlay
                opacity=".06"
                scrim="primary"
                contained
                model-value
                persistent
              />
            </v-card>
          </v-col>

          <v-col cols="12" md="6" sm="12" xs="12">
            <v-card
              append-icon="mdi-open-in-app"
              class="py-4"
              color="surface-variant"
              :to="'/time-database'"
              prepend-icon="mdi-database"
              rel="noopener noreferrer"
              rounded="lg"
              subtitle="Request verification and see newly submitted times."
              title="Time Database"
              variant="text"
            >
              <v-overlay
                opacity=".06"
                scrim="primary"
                contained
                model-value
                persistent
              />
            </v-card>
          </v-col>

          <v-col cols="12" md="6" sm="12" xs="12">
            <v-card
              append-icon="mdi-open-in-app"
              class="py-4"
              color="surface-variant"
              :to="'/live-racing'"
              prepend-icon="mdi-bike"
              rel="noopener noreferrer"
              rounded="lg"
              subtitle="Tools to manage live races and streaming APIs."
              title="Live Racing Tools"
              variant="text"
            >
              <v-overlay
                opacity=".06"
                scrim="primary"
                contained
                model-value
                persistent
              />
            </v-card>
          </v-col>

          <v-col cols="12" md="6" sm="12" xs="12">
            <v-card
              append-icon="mdi-open-in-new"
              class="py-4"
              color="surface-variant"
              href="https://discord.gg/aqwnkgSxPQ/"
              prepend-icon="mdi-account-group-outline"
              rel="noopener noreferrer"
              rounded="lg"
              subtitle="Connect with the Descenders Competitive team."
              target="_blank"
              title="Community"
              variant="text"
            >
              <v-overlay
                opacity=".06"
                scrim="primary"
                contained
                model-value
                persistent
              />
            </v-card>
          </v-col>
          <v-col cols="12" md="3" sm="6" xs="12">
            <v-card
              :loading="total_users_online == 'ERROR'"
              class="py-4"
              color="blue"
              href="">
              <!-- Currently x users online, x times submitted in past 30 days -->
              <v-card-title>
                {{  numberWithCommas(total_users_online) }}
              </v-card-title>
              <v-card-subtitle>
                Users Online
              </v-card-subtitle>
            </v-card>
          </v-col>
          <v-col cols="12" md="3" sm="6" xs="12">
            <v-card
              :loading="times_submitted_past_30_days == 'ERROR'"
              class="py-4"
              color="blue"
              href="">
              <!-- Currently x users online, x times submitted in past 30 days -->
              <v-card-title>
                {{ numberWithCommas(times_submitted_past_30_days) }} 
              </v-card-title>
              <v-card-subtitle>
                times in past 30 days
              </v-card-subtitle>
            </v-card>
          </v-col>
          <v-col cols="12" md="3" sm="6" xs="12">
            <v-card
              :loading="total_stored_times == 'ERROR'"
              class="py-4"
              color="blue"
              href="">
              <v-card-title>
                {{ total_stored_times }}
              </v-card-title>
              <v-card-subtitle>
                total stored times
              </v-card-subtitle>
            </v-card>
          </v-col>
          <v-col cols="12" md="3" sm="6" xs="12">
            <v-card
              :loading="total_replay_size == 'ERROR'"
              class="py-4"
              color="blue"
              href="">
              <v-card-title>
                {{  numberWithCommas(total_replay_size) }}GB
              </v-card-title>
              <v-card-subtitle>
                of stored replays
              </v-card-subtitle>
            </v-card>
          </v-col>
        </v-row>
      </v-responsive>
    </v-container>
</template>

<script setup>
    import { useDisplay } from 'vuetify'
    import { computed } from 'vue'

  // Destructure only the keys you want to use
  const { name } = useDisplay()
  const height = computed(() => {
    // name is reactive and
    // must use .value
    switch (name.value) {
      case 'xs': return 320
      case 'sm': return 470
      case 'md': return 900
      case 'lg': return 900
      case 'xl': return 800
      case 'xxl': return 1200
    }
    return undefined
  })

</script>

<script>
  const apiUrl = import.meta.env.VITE_APP_API_URL;
  import { ref } from 'vue'
 
  export default {
    name: 'App',
    data() {
      return {
        total_replay_size: 'ERROR',
        total_stored_times: 'ERROR',
        total_users_online: 'ERROR',
        times_submitted_past_30_days: 'ERROR'
      }
    },
    mounted() {
      this.$socket.on('message', (data) => {
        try{
          var data_json = JSON.parse(data);
          if (data_json['type'] == 'send'){
            this[data_json['identifier']] = data_json['data'];
          }
        }
        catch (e){
          console.log(e)
        }
      })
      var toUpdate = ['total_replay_size', 'total_stored_times', 'total_users_online', 'times_submitted_past_30_days'];
      toUpdate.forEach((ident) => {
        this.$socket.emit('message', JSON.stringify({
          'type': 'get',
          'identifier': ident
        }));
      })
    },
    methods: {
      numberWithCommas(x) {
        // taken diligently from https://stackoverflow.com/questions/2901102/how-to-format-a-number-with-commas-as-thousands-separators
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      }
    }
  }
</script>