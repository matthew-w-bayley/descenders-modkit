<template>
    <v-container justify="center">
    <v-alert
        border="left"
        color="red"
        type="error"
        v-if="timeInfo.name == null"
    >This time could not be found in the database!</v-alert>
    <v-card>
        <v-card-title class="text-center">
            <h2>{{ secs_to_str(timeInfo.time) }}</h2>
            <h3>{{ timeInfo.name }}</h3>
        </v-card-title>
        <v-card-subtitle class="text-center">
            Time ID: {{ timeInfo.time_id }}
        </v-card-subtitle>
        <v-card-subtitle  class="text-center">
            World Name: {{ timeInfo.world_name }}
        </v-card-subtitle>
        <v-card-subtitle class="text-center">
            Submitted: {{ new Date(timeInfo.submission_timestamp * 1000).toLocaleString() }}
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
            <v-chip
                :color="timeInfo.replay_exists ? 'green' : 'red'"
                outlined
            >
                <v-icon start>{{ timeInfo.replay_exists ? 'mdi-check' : 'mdi-close' }}</v-icon>
                Replay exists
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
        <v-divider class="my-4"></v-divider>
        <v-card-actions>
          <!-- report button on top right-->
          <v-btn disabled @click="report = !report" icon class="position-absolute top-0 right-0" color="orange" v-bind="attrs" v-on="on"><v-icon>mdi-flag</v-icon></v-btn>
          <v-spacer></v-spacer>
          <v-btn :href="'/api/download-replay/' + timeInfo.time_id"><v-icon>mdi-download-circle</v-icon>Replay</v-btn>
        </v-card-actions>
      </v-card>
    </v-container>
      
    <v-overlay z-index="3000" v-model="report" class="d-flex justify-center align-center">
      <v-card>
        <v-card-title class="text-center">Report Issue</v-card-title>
        <v-card-text>
          <v-form>
            <v-select
              v-model="reportType"
              :items="['No Replay', 'Cheating', 'Invalid Time', 'Innapropriate Username']"
              label="Type"
              required
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="submitReport">Submit</v-btn>
          <v-btn @click="report = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-overlay>
</template>  
  
<script>
    export default {
        data: () => ({
            timeInfo: {},
            report: false,
        }),
        mounted() {
            this.$socket.emit("message", {"type": "get", "identifier": "time", "data": this.$route.params.time_id});
            this.$socket.on("message", (data) => {
                var data_json = JSON.parse(data);
                if (data_json["type"] == "send"){
                    if (data_json["identifier"] == "time"){
                        this.timeInfo = data_json["data"];
                    }
                }
            });
        },
        methods: {
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
            submitReport(){
                this.$socket.emit("message", {"type": "report", "identifier": "time", "data": {"time_id": this.timeInfo.time_id, "report_type": this.reportType}});
                this.report = false;
            }
        }
    }
</script>