<template>
  <v-container fluid width="100%"
  height="90%">

  <v-container
    width="100%"
    height="80vh"
    class="d-flex justify-center d-sm-flex"
  >      

      <v-data-table-server
          width="100%"
          height="100%"

          v-model:items-per-page="itemsPerPage"
          :headers="headers"
          :items="serverItems"
          :items-length="totalItems"
          :loading="loading"
          :search="search"
          item-value="name"
          @update:options="loadItems"
          :sort-by="sortBy" 
        >
        <template v-slot:item.verified="{ item }">
          <v-icon v-if="item.verified" color="success">mdi-check</v-icon>
          <v-icon v-else color="error">mdi-close</v-icon>
        </template>
        <template v-slot:item.deleted="{ item }">
          <v-icon v-if="item.deleted" color="success">mdi-check</v-icon>
          <v-icon v-else color="error">mdi-close</v-icon>
        </template>
        <template v-slot:item.submission_timestamp="{ item }">
          {{ new Date(item.submission_timestamp * 1000).toLocaleString() }}
        </template>
        <template v-slot:item.time_id="{ item }">
          <v-btn target="_blank" @click="focusTime = item">
            <v-icon>mdi-open-in-new</v-icon>
          </v-btn>
        </template>
        <template v-slot:item.time="{ item }">
          {{ secs_to_str(item.time) }}
        </template>
        <!-- overlay -->

      </v-data-table-server>
      <template>
        <TimeOverlay v-model:timeInfo="focusTime" />
      </template>
    </v-container>
  </v-container>
  </template>  

<script>
export default {
  data: () => ({
    itemsPerPage: 10,
    sortBy: [{ key: 'submission_timestamp', order: 'desc' }],
    headers: [
      { title: 'Player Name', key: 'name', align: 'start' },
      { title: 'Bike Type', key: 'bike', align: 'end' },
      { title: 'Deleted', key: 'deleted', align: 'end' },
      { title: 'Verified', key: 'verified', align: 'end' },
      { title: 'Modkit Version', key: 'version', align: 'end' },
      { title: 'Time', key: 'time', align: 'center' },
      { title: 'Submission Date', key: 'submission_timestamp', align: 'end' },
      { title: '', key: 'time_id', align: 'end' },
    ],
    search: '',
    serverItems: [],
    loading: true,
    totalItems: 0,
    focusTime: null,
    abortController: null, // Store AbortController instance
  }),

  methods: {
    async loadItems({ page, itemsPerPage, sortBy }) {
      this.serverItems = [];
      // Cancel previous request if it exists
      if (this.abortController) {
        console.log("Aborting previous request...");
        this.abortController.abort();
      }

      // Create a new AbortController
      this.abortController = new AbortController();
      const { signal } = this.abortController;

      this.loading = true;

      try {
        console.log("Fetching data...");
        const { items, total } = await this.fetchItems({ page, itemsPerPage, sortBy, signal });

        // Only update if this request wasn't aborted
        if (!signal.aborted) {
          this.serverItems = items;
          this.totalItems = total;
        }
      } catch (error) {
        if (error.name === "AbortError") {
          console.log("Request aborted, ignoring response.");
        } else {
          console.error("Error fetching data:", error);
        }
      } finally {
        this.loading = false;
      }
    },

    async fetchItems({ page, itemsPerPage, sortBy, signal }) {
      const params = new URLSearchParams({
        page: page,
        items_per_page: itemsPerPage,
        sort_by: sortBy.length ? sortBy[0].key : '',
        order: sortBy.length ? (sortBy[0].order === 'desc' ? 'desc' : 'asc') : '',
      });
      var apiUrl = "http://localhost:8082"
      console.log("API Call:", `${apiUrl}/get-all-times?${params.toString()}`);
      
      const resp = await fetch(`${apiUrl}/get-total-stored-times`, { signal });
      const num_tot = await resp.json();

      const response = await fetch(`${apiUrl}/get-all-times?${params.toString()}`, { signal });
      const data = await response.json();

      console.log("Fetched items:", data.length);

      return { items: data, total: num_tot };
    },

    secs_to_str(secs) {
      secs = parseFloat(secs);
      var d_mins = Math.floor(secs / 60);
      var d_secs = Math.floor(secs % 60);
      var fraction = secs * 1000;
      fraction = Math.round(fraction % 1000);
      d_mins = d_mins.toString();
      d_secs = d_secs.toString();
      fraction = fraction.toString();
      if (d_mins.length == 1) d_mins = "0" + d_mins.toString();
      if (d_secs.length == 1) d_secs = "0" + d_secs;
      while (fraction.length < 3) fraction = "0" + fraction;
      return d_mins + ":" + d_secs + "." + fraction;
    },
  },
};

</script>