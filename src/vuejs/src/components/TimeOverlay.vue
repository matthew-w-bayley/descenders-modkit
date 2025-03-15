<template>
    <!-- Overlay that shows time info -->
    <v-overlay v-model="overlay" class="d-flex justify-center align-center">
      <v-card
        v-if="timeInfo != null"
        min-width="500px">
        <v-card-title class="text-center">
          {{ timeInfo.name }}
        </v-card-title>
        <v-card-subtitle class="text-center">
          ID {{ timeInfo.time_id }}
        </v-card-subtitle>
        <v-card-actions class="justify-center">
            <v-chip
                :color="timeInfo.deleted ? 'red' : 'green'"
                text-color="white"
                class="ma-2"
                outlined
            >
                <v-icon start>{{ timeInfo.deleted ? 'mdi-exclamation' : 'mdi-close' }}</v-icon>
                Deleted
            </v-chip>
            <v-chip
                :color="timeInfo.verified ? 'green' : 'red'"
                text-color="white"
                class="ma-2"
                outlined
            >
                <v-icon start>{{ timeInfo.verified ? 'mdi-check' : 'mdi-close' }}</v-icon> 
                Verified
            </v-chip>
            <v-chip
                :color="timeInfo.bike == 0 ? 'blue' : timeInfo.bike == 1 ? 'pink' : 'orange'"
            >
                <v-icon start>mdi-bike</v-icon>
                {{ timeInfo.bike == 0 ? 'Enduro' : timeInfo.bike == 1 ? 'Downhill' : 'Hardtail' }}
            </v-chip>
            <v-chip>
                <v-icon start>mdi-speedometer</v-icon>
                {{ Math.round(timeInfo.starting_speed) }}m/s
            </v-chip>
            <v-chip>
                <v-icon start>mdi-developer-board</v-icon>
                Version {{ timeInfo.version }}
            </v-chip>
        </v-card-actions>
        
        <v-card-actions>
          <!-- report button on top right-->
          <v-btn disabled @click="report = !report" icon class="position-absolute top-0 right-0" color="orange" v-bind="attrs" v-on="on"><v-icon>mdi-flag</v-icon></v-btn>
          <v-btn @click="clearTime();">Close</v-btn>
          <v-spacer></v-spacer>
          <v-btn :href="'/time/' + timeInfo.time_id"><v-icon>mdi-open-in-new</v-icon></v-btn>
          <v-spacer></v-spacer>
          <v-btn :href="'/api/download-replay/' + timeInfo.time_id"><v-icon>mdi-download-circle</v-icon>Replay</v-btn>
        </v-card-actions>
      </v-card>
    </v-overlay>
</template>

<script>
export default {
    props: {
        timeInfo: Object,
    },
    emits: ["update:timeInfo"],
    computed: {
        overlay() {
            return this.timeInfo != null;
        }
    },
    methods: {
      clearTime(){
        this.$emit('update:timeInfo', null)
      }
    }
}
</script>
  
