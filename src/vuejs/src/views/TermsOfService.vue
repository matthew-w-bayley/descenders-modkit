<template>
  <v-container>
    <v-card class="pa-4">
      <v-card-title class="text-h5">Terms of Service</v-card-title>
      <v-card-subtitle>Last Updated: 27th March 2025</v-card-subtitle>
      <v-divider class="mb-4"></v-divider>
      <v-scroll-y-transition>
        <v-card-text>
          <p>Welcome to the Descenders Modkit ("Application"). By using this Application, you agree to these Terms of Service ("Terms"). If you do not agree, do not use the Application.</p>

          <v-divider class="my-3"></v-divider>
          <h3 class="text-h6">1. Use of the Application</h3>
          <p>The Application is provided "as is" without any guarantees of performance or stability.</p>
          <p>The Application has the ability to crash or close your game as part of its normal operation. You acknowledge that this is an inherent risk of using the software.</p>
          <p>The developers are not responsible for any loss of data, game progress, or other consequences resulting from use of the Application.</p>
          <p>You may not use the Application for any unlawful purposes or modify it in ways not intended by the developers.</p>
          <p>You will not use exploits or illegal or unauthorized means to interfere with or adversely impact any other user's ability to use the Services as intended; to gain unfair gameplay advantage; or to gain access to Virtual Items or other Content to which you do not have valid entitlement. This includes the use of cheats or so-called “mod menus”, unauthorized mods, hacks, glitches, or any other technical exploits, and phishing, scamming, or social engineering.</p>

          <v-divider class="my-3"></v-divider>
          <h3 class="text-h6">2. Telemetry and Data Collection</h3>
          <p>The Application tracks telemetry data, including but not limited to system information, public IP, game performance, crash reports, and usage analytics.</p>
          <p>This data is collected to improve the Application and diagnose potential issues.</p>
          <p>By using the Application, you consent to this data collection and usage.</p>

          <v-divider class="my-3"></v-divider>
          <h3 class="text-h6">3. Disclaimer of Warranties & Limitation of Liability</h3>
          <p>The developers make no warranties regarding the Application's availability, security, or fitness for any particular purpose.</p>
          <p>The developers are not responsible for any direct, indirect, incidental, or consequential damages resulting from your use of the Application.</p>

          <v-divider class="my-3"></v-divider>
          <h3 class="text-h6">4. Updates and Changes</h3>
          <p>The developers may update these Terms at any time. Continued use of the Application after changes means you accept the new Terms.</p>
          <p>The developers may modify or discontinue the Application at any time without notice.</p>

          <v-divider class="my-3"></v-divider>
          <h3 class="text-h6">5. Governing Law</h3>
          <p>These Terms shall be governed by and interpreted in accordance with the laws of the United Kingdom of Great Britain and Northern Ireland.</p>

          <h3 class="text-h6">6. Enforcement & Penalties</h3>
          <p>The developers and authorized users reserve the right to take action against users who violate these Terms.</p>
          <p>This includes, but is not limited to:</p>
          <ul>
            <li>Banning users from using the Application.</li>
            <li>Removing or modifying leaderboard times for any reason (particularly if unfair advantages, exploits, or cheating are detected).</li>
            <li>Closing or forcefully terminating the game session (particularly if unauthorized modifications or exploits are detected).</li>
          </ul>
          <p>Decisions regarding enforcement are final and made at the discretion of any users authorized by developers.</p>
        </v-card-text>
      </v-scroll-y-transition>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: "TermsOfService",
};
</script>

<style scoped>
p {
  margin-bottom: 10px;
}
</style>