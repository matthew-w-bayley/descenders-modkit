<template>
<v-app-bar app extension-height="100%">
    <v-container fluid>
        <v-row  align="center" justify="space-between">
        <v-col cols="auto">
            <router-link to="/">
            <img src="@/assets/logo.png" alt="Descenders Modkit Logo" height="40" />
            </router-link>
        </v-col>
        <v-col class="d-none d-md-flex">
            <template v-for="route in routes">
            <v-btn
                v-if="route.name !== 'Home' && route.inHomeBar === true"
                text
                :to="route.path"
                :key="route.name"
                :disabled="route.name === 'Leaderboard'"
            >{{ route.name }}</v-btn>
            </template>
        </v-col>
        <v-col v-if="xs || sm">
            <v-app-bar-nav-icon @click.stop="drawer = !drawer">

            </v-app-bar-nav-icon>
        </v-col>
 
        
        <Settings />

        </v-row>

    </v-container>
        
        <v-spacer />
        
        <template v-slot:extension v-if="!isOnline">
            <TopBanner />
        </template>
    </v-app-bar>

    <v-navigation-drawer
        v-model="drawer"
        app
        left
        v-if="xs || sm"
    >
        <v-list>
            <v-list-item
                v-for="route in routes"
                :to="route.path"
                :key="route.name"
                link
            >
                <v-list-item-title>{{ route.name }}</v-list-item-title>
                
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
</template>

<script>
import { routes } from '@/router'
    export default {
        name: 'App',
        data() {
        return {
            routes,
            darkMode: true,
            drawer: false,
        }
    }
}
</script>

<script setup>
  import { useDisplay } from 'vuetify'
  const apiUrl = import.meta.env.VITE_APP_API_URL;
  
  const { xs, sm } = useDisplay()

  var isOnline = true;
  fetch(`${apiUrl}/get-trails`)
    .then(data => {
        isOnline = true;
    })
    .catch(error => {
        isOnline = false;
    });
</script>