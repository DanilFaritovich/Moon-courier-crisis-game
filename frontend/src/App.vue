<script setup lang="ts">
import GameView from "./views/GameView.vue";
</script>

<template>
  <GameView />
</template>

<style>
.map-node.assigned .order-tag {
  fill: #71808a;
}

.map-node.assigned circle:not(.pulse) {
  fill: #283640;
  stroke: #65757f;
}
</style>
