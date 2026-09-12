<script setup lang="ts">
defineProps<{
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  distance: number;
  risk: number;
}>();
</script>
<template>
  <g class="map-edge"
    ><line :x1="x1" :y1="y1" :x2="x2" :y2="y2" /><text
      :x="(x1 + x2) / 2"
      :y="(y1 + y2) / 2 - 9"
      >{{ distance }} km · {{ Math.round(risk * 100) }}% risk</text
    ></g
  >
</template>
