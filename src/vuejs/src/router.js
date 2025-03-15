import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import Leaderboard from './views/Leaderboard.vue';
import LiveRacing from './views/LiveRacing.vue';
import LiveRacingTag from './views/LiveRacingTag.vue';
import LiveRacingTime from './views/LiveRacingTime.vue';
import TimeDatabase from './views/TimeDatabase.vue';
import Callback from './views/Callback.vue'
import Time from './views/Time.vue';

const routes = [
  { path: '/', name: 'Home', component: Home, inHomeBar: false },
  { path: '/leaderboard', name: 'Leaderboard', component: Leaderboard, inHomeBar: true },
  { path: '/time-database', name: 'Time Database', component: TimeDatabase, inHomeBar: true },
  { path: '/live-racing', name: 'Live Racing', component: LiveRacing, inHomeBar: true },
  { path: '/callback', name: 'Callback', component: Callback, inHomeBar: false},
  { path: '/live-racing/spectated-player/', name: 'Spectated Player', component: LiveRacingTag, inHomeBar: false},
  { path: '/time/:time_id', name: 'Time', component: Time, inHomeBar: false },
  { path: '/live-racing/spectated-player-time', name: 'Live Racing Time', component: LiveRacingTime, inHomeBar: false },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// if path is /live-racing and user isn't authenticated, redirect to discord.py
const token = localStorage.getItem("discord_token");
const REDIRECT_URI = encodeURIComponent("https://modkitv2.nohumanman.com/callback");
router.beforeEach((to, from, next) => {
  if (to.path === '/live-racing' && !token) {
    next();//window.location.href = `https://discord.com/api/oauth2/authorize?client_id=973689949020880926&redirect_uri=${REDIRECT_URI}&response_type=token&scope=identify`;
  } else {
    next();
  }
});

export default router;
export { routes }; // Export routes for use in the App.vue component
