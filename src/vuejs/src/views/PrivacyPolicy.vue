<template>
  <v-container>
    <v-card class="pa-4">
      <v-card-title class="text-h5">Privacy Policy</v-card-title>
      <v-card-subtitle>Last Updated: 15th March 2025</v-card-subtitle>
      <v-divider class="mb-4"></v-divider>
      <v-scroll-y-transition>
        <v-card-text>
          <h3 class="text-h6">1. Information We Collect</h3>
          <p>The Application collects the following types of data:</p>
          <ul>
            <li>System information (hardware specs, operating system details)</li>
            <li>Player information (steam id, guid)</li>
            <li>Replay files (files located in the replays folder of Descenders)</li>
            <li>Game performance metrics</li>
            <li>Crash reports and error logs</li>
            <li>General usage analytics (such as feature engagement)</li>
          </ul>
          
          <v-divider class="my-3"></v-divider>
          <h3 class="text-h6">2. How We Use Your Information</h3>
          <p>To monitor and improve the performance of the Application</p>
          <p>To identify and diagnose crashes or issues</p>
          <p>To understand how users interact with the Application</p>
          
          <v-divider class="my-3"></v-divider>
          <h3 class="text-h6">3. Data Sharing & Security</h3>
          <p>Collected data is used internally and is not sold to third parties.</p>
          <p>We take reasonable steps to protect your data but cannot guarantee absolute security.</p>
          
          <v-divider class="my-3"></v-divider>
          <h3 class="text-h6">4. Your Choices</h3>
          <p>If you do not want telemetry data collected, <b>you must discontinue use of the Application</b>.</p>
          
        </v-card-text>
      </v-scroll-y-transition>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: "PrivacyPolicy",
};
</script>

<style scoped>
p {
  margin-bottom: 10px;
}
ul {
  padding-left: 20px;
}
li {
  margin-bottom: 5px;
}
</style>